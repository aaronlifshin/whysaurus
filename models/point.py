""" Main database entities 

A summary of how the main database entities work is below:

POINTS AND POINT ROOTS:
Point class represents a single version of a point, to be displayed on the point page
PointRoot class represents an ancestor of all the versions of a single point
Other points can reference the pointRoot key as a stable reference for the point
The current version of the point is kept in two places, the .current of the point class 
A key reference to the current point in the PointRoot
The URL is a unique way to get a pointRoot (but if it changes, a redirect is created)

LINKS:
When a point links to another, the link is recorded in three(!) ways
 1. In the linking point, a link to the root is recorded in the [linkType]PointsRoots array
 2. In the linking point, a link to the version current at that time is recorded in the [linkType]PointsLastChange array
 3. In the linked point, a backlink to the root is recorded

When a link is removed, the backlink is placed into an archive, so that when points are deleted, 
we know where roots were

The backlinks are in the pointRoot and reflect the current version

"""
from __future__ import division

import re
import logging
import math

from google.appengine.ext import ndb
from google.appengine.ext.db import BadRequestError, TransactionFailedError
from google.appengine.api import search
from google.appengine.api.taskqueue import Task
from google.appengine.ext import deferred

from imageurl import ImageUrl
from whysaurusexception import WhysaurusException
from redirecturl import RedirectURL
from source import Source
from timezones import PST
from follow import Follow
from uservote import RelevanceVote
from comment import Comment 


def convertListToKeys(urlsafeList):
    if urlsafeList:
        outList = []
        for u in urlsafeList:
            outList = outList + [ndb.Key(urlsafe=u)]
        return outList 
    else:
        return None
        
"""
Every point must have a unique URL
If it already exists, add a number, and store how many times this URL existed, 
  so number can be added next time
Also check redirects
(Redirects are created when a URL of a point changes)

"""
def makeURL(sourceStr):
    longURL = sourceStr.replace(" ", "_")
    newUrl = re.sub('[\W]+', '', longURL[0:140])
    # Check if it already exists
    pointRootQuery = PointRoot.gql("WHERE url= :1", newUrl)
    pointRoot = pointRootQuery.get()
    
    if pointRoot:
        # Existing URL notes how many URLs+number exist for that URL
        pointRoot.numCopies = pointRoot.numCopies + 1
        newUrl = newUrl + str(pointRoot.numCopies)
        pointRoot.put()
    else:
        redirectQuery = RedirectURL.gql("WHERE fromURL= :1", newUrl)
        redirectURL = redirectQuery.get()
        if redirectURL:
            redirectURL.numCopies = redirectURL.numCopies + 1
            newUrl = newUrl + str(redirectURL.numCopies)
            redirectURL.put()        
    return newUrl
  
@ndb.tasklet
def getCurrent_async(pointRoot):
    if pointRoot:
        current = yield pointRoot.current.get_async()
        raise ndb.Return(current)
    else:
        raise ndb.Return(None)
            
class Link(ndb.Model):
    version = ndb.KeyProperty(indexed=False)
    root = ndb.KeyProperty(indexed=False)
    # rating = ndb.IntegerProperty(indexed=False)
    voteCount = ndb.IntegerProperty(indexed=False)
    fRating = ndb.FloatProperty(indexed=False) # relevancy score
    
    @property
    def rating(self):
        return int(round(self.fRating, 0)) if self.fRating else 0
        
    def updateRelevanceData(self, oldRelVote, newRelVote):
        startingRating = self.fRating if self.fRating else 0
        if oldRelVote:
            # this user has already voted
            newSum = startingRating * self.voteCount - oldRelVote.value + newRelVote.value
            self.fRating = newSum/self.voteCount                    
        else:
            newSum = startingRating * self.voteCount + newRelVote.value
            self.voteCount = self.voteCount + 1
            self.fRating = newSum/self.voteCount
        

class Point(ndb.Model):
    """Models an individual Point with an author, content, date and version."""
    # creator is the creator of the first version of this Point (perhaps this should be stored on pointRoot? -JF)
    creatorURL = ndb.StringProperty(indexed=False)
    creatorName = ndb.StringProperty(indexed=False)

	# author is the creator of *this version* of this Point 
    authorName = ndb.StringProperty(indexed=False)
    authorURL = ndb.StringProperty(indexed=False)
	
    content = ndb.TextProperty(indexed=False)
    summaryText = ndb.TextProperty(indexed=False)  # This is Text not String because I do not want it indexed
    title = ndb.StringProperty(indexed=False)
    dateEdited = ndb.DateTimeProperty(auto_now_add=True) # Order by used
    version = ndb.IntegerProperty(default=1) # Order by used
    # supportingPoints = ndb.KeyProperty(repeated=True) # DEPRECATED
    
    supportingLinks = ndb.StructuredProperty(Link, repeated=True)    
    counterLinks = ndb.StructuredProperty(Link, repeated=True)    
    usersContributed = ndb.StringProperty(repeated=True)
        
    sources = ndb.KeyProperty(repeated=True, indexed=False)
    current = ndb.BooleanProperty() # used in filter queries
    url = ndb.StringProperty(indexed=False)
    upVotes = ndb.IntegerProperty(default=1, indexed=False)
    downVotes = ndb.IntegerProperty(default=0, indexed=False)
    voteTotal = ndb.IntegerProperty(default=1) # used in sorting
    ribbonTotal = ndb.IntegerProperty(default=0) # used in sorting
    imageURL = ndb.StringProperty(default='', indexed=False)
    summaryMediumImage = ImageUrl('SummaryMedium')
    summaryBigImage = ImageUrl('SummaryBig')
    fullPointImage = ImageUrl('FullPoint')
    imageDescription = ndb.StringProperty(default='', indexed=False)
    imageAuthor = ndb.StringProperty(default='', indexed=False)
    _vote = None
    _relevanceVote = None
    _linkInfo = None
    isTop = ndb.BooleanProperty(default=True)
    

    @property
    def numSupporting(self):
        return len(self.supportingLinks) if self.supportingLinks else 0
        
    @property
    def numCounter(self):
        return len(self.counterLinks) if self.counterLinks else 0
 
    def numSupportingPlusCounter(self):
        return self.numSupporting + self.numCounter  
        
    def pointValue(self):
        """
        Scalar [0-100ish] property that weighs how 'good' the point is,
        incorporating:
        +1 for including a source
        + having agrees >= disagrees
        + having sub-arguments weighed in its favor
        """
        return (min(1, len(self.sources))
                + self.upVotes - self.downVotes
                + self.getChildrenPointRating())

    @property
    def linksRatio(self):
        sup = self.numSupporting
        cou = self.numCounter
        if sup == 0 and cou == 0:
            return 50
        elif cou == 0:
            return 80 # I think this ceiling is a vestige of the "gauge" UI element we built once that no longer exists - JF
        elif sup == 0:
            return 20 # I think this floor is a vestige of the "gauge" UI element we built once that no longer exists - JF
        else:
            rat1 = sup/float(sup + cou)
            return math.floor(rat1*100) # Django widthratio requires integers

    @property
    def numUsersContributed(self):
        if self.usersContributed is None or len(self.usersContributed) == 0:
            return None
        return len(self.usersContributed)

    # Gene: Temporary until we script the creatorName population
    @property
    def creatorOrAuthorName(self):
        if self.creatorName is None or len(self.creatorName) == 0:
            return self.authorName
        return self.creatorName

    # Gene: Temporary until we script the creatorName population
    @property
    def creatorOrAuthorURL(self):
        if self.creatorURL is None or len(self.creatorURL) == 0:
            return self.authorURL
        return self.creatorURL

    @property
    def dateEditedText(self):
        return self.PSTdateEdited.strftime('%b. %d, %Y, %I:%M %p')
        
    @property
    def PSTdateEdited(self):
        return PST.convert(self.dateEdited)
    
    @property
    def reverseLinksRatio(self):
        return 100 - self.linksRatio
        
    @property
    def rootURLsafe(self):
        return self.key.parent().urlsafe();
        
    @property
    def relevancePercent(self):
        if self._linkInfo is None or self._linkInfo.voteCount == 0:
            return 'Please Set' 
        else:
            return str(self._linkInfo.rating) + '%'
            
    @property
    def belowRelevanceThreshold(self):
        if self._linkInfo is None or self._linkInfo.voteCount == 0:
            return False 
        else:
            return self._linkInfo.rating < 33
    
    @property
    def relevanceVoteCount(self):
        return 0 if self._linkInfo is None else self._linkInfo.voteCount
        
    @property
    def vote(self):
        return 0 if self._vote is None else self._vote
        
    @property
    def myVoteValue(self):
        if self._relevanceVote is None:
            return None
        else:
            return self._relevanceVote.value
        
    @classmethod
    def getByKey(cls, pointKey):
        return ndb.Key('Point', pointKey).get()

    """
    This adds a task to a queue to notify users of a change in the point
    The /addNotification task will notify all the users that are following the point
    """
    @classmethod
    def addNotificationTask(cls, pointRootKey, userKey, notifyReasonCode, additionalText=None):
        taskParams = {'rootKey':pointRootKey.urlsafe(),
                         'userKey':userKey.urlsafe(),
                         'notifyReasonCode': notifyReasonCode }
        if additionalText:
            taskParams['additionalText'] = additionalText
        t = Task(url='/addNotifications', 
                 params=taskParams)
        t.add(queue_name="notifications", transactional=ndb.in_transaction())
        
    @staticmethod
    def getCurrentByUrl(url):
        pointRootQuery = PointRoot.gql("WHERE url= :1", url)
        pointRoot = pointRootQuery.get()
        point = None        
        if pointRoot:
            point = pointRoot.getCurrent()
                        
        if point:
            return point, pointRoot
        else:
            return (None, None)
    
    # This method will check redirects and yield
    @staticmethod
    @ndb.tasklet
    def findCurrent_async(url):
        q = PointRoot.query(PointRoot.url == url)
        pointRoot = yield q.get_async()
        if pointRoot:
            point = yield getCurrent_async(pointRoot)            
            raise ndb.Return(point, pointRoot)            
        else:
            # Try to find a redirector
            newRedirectURL = yield RedirectURL.getByFromURL_asynch(url)
            if newRedirectURL:
                q = PointRoot.query(PointRoot.url == newRedirectURL.toURL)
                pointRoot = yield q.get_async()
                if pointRoot:
                    point = yield getCurrent_async(pointRoot)                
                    raise ndb.Return(point, pointRoot)
                else:
                    raise ndb.Return(None, None)                            
            else:
                raise ndb.Return(None, None)                            

    @staticmethod
    def getCurrentByRootKey(rootKey):
        pointRoot = ndb.Key(urlsafe=rootKey).get()
        point = pointRoot.getCurrent()
        return point, pointRoot

    @classmethod
    def getFullHistory(cls, url):
        pointRoot = PointRoot.query(PointRoot.url == url).get()
        if pointRoot:
            # Just most recent 50 for now
            points = Point.query(ancestor=pointRoot.key).order(
                -Point.version).fetch(50)
            # Image code left commented for when multiple images are added
            # images = PointImage.query(ancestor=pointRoot.key).fetch(50)
            retVal = []
            for point in points:
                supportingPointsLastVersion = point.getLinkedPointsLastChange("supporting")
                counterPointsLastVersion = point.getLinkedPointsLastChange("counter")
                sources = point.getSources()

                # pointImages = [image for image in images if image.key.parent() == point.key]
                # image = None
                # if pointImages:
                #   image = pointImages[0]
                retVal.append({"point": point,
                               "supportingPoints": supportingPointsLastVersion,
                               "counterPoints": counterPointsLastVersion,
                               "sources":sources })  # , "image":image})
            return retVal
        else:
            return None
            
    @staticmethod
    @ndb.transactional(xg=True)
    def transactionalCreate(pointRoot, title, content, summaryText, user,
                            imageURL=None, imageAuthor=None, 
                            imageDescription=None, sourceURLs=None, sourceNames=None, isTop=False):
        pointRoot.put()
        point = Point(parent=pointRoot.key)
        point.title = title
        point.url = pointRoot.url
        point.content = content
        point.summaryText = summaryText if (len(
            summaryText) != 250) else summaryText + '...'
        point.authorName = user.name
        point.authorURL = user.url
        point.creatorName = user.name
        point.creatorURL = user.url
        point.version = 1
        point.current = True
        point.upVotes = 0
        point.downVotes = 0
        point.voteTotal = 0
        point.imageURL = imageURL
        point.imageDescription = imageDescription
        point.imageAuthor = imageAuthor
        point.isTop = isTop
        point.put() 
        sources = None
        if sourceURLs and sourceNames:
            sources = Source.constructFromArrays(sourceURLs, sourceNames, point.key)
        if sources:
            sourceKeys = []
            for source in sources:
                source.put()
                sourceKeys = sourceKeys + [source.key]
            point.sources = sourceKeys
        point.put()
        point.addToSearchIndexNew()

        pointRoot.current = point.key
        pointRoot.isTop = isTop
        pointRoot.put()

        # No automatic agreement
        # user.addVote(point, voteValue=1, updatePoint=False)
        user.recordCreatedPoint(pointRoot.key)
        
        return point, pointRoot

    @staticmethod
    def create(title, content, summaryText, user, backlink=None, linktype="",
               imageURL=None, imageAuthor=None, imageDescription=None, 
               sourceURLs=None, sourceNames=None, urlToUse = None):
        
        newUrl = urlToUse if urlToUse else makeURL(title) 
        pointRoot = PointRoot()
        pointRoot.url = newUrl
        pointRoot.numCopies = 0
        pointRoot.editorsPick = False
        pointRoot.viewCount = 1
        isTop = True
        if backlink:
            logging.info('- - -- -  Creating with a BL')
            isTop = False
            if linktype == 'supporting':
                pointRoot.pointsSupportedByMe = [backlink]
            elif linktype == 'counter':
                pointRoot.pointsCounteredByMe = [backlink]
        else:
            logging.info('-NO BL FOUND')
                
        createdPoint, createdPointRoot = Point.transactionalCreate(
                            pointRoot, title, content, summaryText, user,
                            imageURL, imageAuthor, imageDescription, 
                            sourceURLs, sourceNames, isTop = isTop)

        # Only do this if we are not inside of a transaction
        if urlToUse is None:
            Follow.createFollow(user.key, createdPointRoot.key, "created")

        return createdPoint, createdPointRoot

    @staticmethod
    def createTree(dataForPointTree, user):
        for p in dataForPointTree:
            newUrl = makeURL(p['title'])
            p['url'] = newUrl
        newPoint, newPointRoot = Point.transactionalCreateTree(dataForPointTree, user)
        if newPointRoot:
            for p in dataForPointTree:
                Follow.createFollow(user.key, p['pointRoot'].key, "created")
        return newPoint, newPointRoot 

    @staticmethod
    @ndb.transactional(xg=True)
    def transactionalCreateTree(dataForPointTree, user):
        outlineRoot = OutlineRoot()
        outlineRoot.put()
        # ITERATE THE FIRST TIME AND CREATE ALL POINT ROOTS WITH BACKLINKS
        for p in dataForPointTree:
            pointRoot = PointRoot(parent=outlineRoot.key)
            pointRoot.url = p['url']
            pointRoot.numCopies = 0
            pointRoot.editorsPick = False
            pointRoot.viewCount = 1
            if 'parentIndex' in p:
                parentPointRoot = dataForPointTree[p['parentIndex']]['pointRoot']
                pointRoot.pointsSupportedByMe = [parentPointRoot.key]
            pointRoot.put()
            p['pointRoot'] = pointRoot
            point = Point(parent=pointRoot.key)
            point.title = p['title']
            point.url = pointRoot.url
            point.content = p['furtherInfo']
            point.current = True
            point.authorName = user.name
            point.authorURL = user.url
            point.creatorName = user.name
            point.creatorURL = user.url
            point.put()
            user.addVote(point, voteValue=1, updatePoint=False)
            user.recordCreatedPoint(pointRoot.key)
            p['point'] = point
            p['pointRoot'].current = p['point'].key            
            pointRoot.put()
            point.addToSearchIndexNew()
                    
        # ITERATE THE SECOND TIME ADD SUPPORTING POINTS
        for p in dataForPointTree:
            if 'parentIndex' in p:
                linkP = dataForPointTree[p['parentIndex']]['point']
                newLink = Link( 
                    version = p['point'].key,
                    root = p['pointRoot'].key,
                    voteCount = 0
                )
                linkP.supportingLinks = linkP.supportingLinks + [newLink] if \
                    linkP.supportingPointsRoots else [newLink]
                    
                # OLD STORAGE SYSTEM
                linkP.supportingPointsRoots = linkP.supportingPointsRoots + [p['pointRoot'].key] \
                    if linkP.supportingPointsRoots else [p['pointRoot'].key]
                linkP.supportingPointsLastChange = linkP.supportingPointsLastChange + [p['point'].key] \
                    if linkP.supportingPointsRoots else [p['point'].key]

        # ITERATE THE THIRD TIME AND WRITE POINTS WITH ALL SUPPORTING POINTS AND SOURCE KEYS 
        for p in dataForPointTree:
            if p['sources']:
                sourceKeys = []
                for s in p['sources']:
                    source = Source(parent=p['point'].key)
                    source.url = s['sourceURL']
                    source.name = s['sourceTitle']
                    source.put()
                    sourceKeys = sourceKeys + [source.key]
                p['point'].sources = sourceKeys
            p['point'].put()
        
        return dataForPointTree[0]['point'], dataForPointTree[0]['pointRoot']

                        

    def shortJSON(self):
        return {"title":self.title,
                "url": self.url,
                "voteTotal":self.voteTotal,
                "imageURL":self.imageURL,
                "summaryMediumImage":self.summaryMediumImage
                }
                

    def linkCount(self, linkType):
        linkCol = self.getStructuredLinkCollection(linkType)
        return len(linkCol) if linkCol else 0

    def getStructuredLinkCollection(self, linkType):
        if linkType == 'supporting':
            return self.supportingLinks            
        elif linkType == 'counter':
            return self.counterLinks            
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)
            
    # SET THE STRUCTURE LINK COLLECTION BY LINK TYPE
    def setStructuredLinkCollection(self, linkType, linkCollection):
        if linkType == 'supporting':
            self.supportingLinks = linkCollection
        elif linkType == 'counter':
            self.counterLinks = linkCollection
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)

    # RETURN ROOT LINK COLLECTION ONLY FOR SUPPLIED LINK TYPE          
    def getLinkedPointsRootKeys(self, linkType):
        linkColl = self.getStructuredLinkCollection(linkType)
        return [link.root for link in linkColl]

    # DATASTORE GET OF THE CURRENT VERSION OF THE LINKED POINT BY LINK NAME
    #   GOES THROUGH THE ROOT TO GET THE CURRENT POINT AT TIME OF CALL
    #   IF A USER IS SUPPLIED, WILL ALSO ATTACH THE RELEVANCE VOTES OF THAT USER
    #   INTO THE STRUCTURES OF THE POINTS
    def getLinkedPoints(self, linkType, user):
        linkColl = self.getStructuredLinkCollection(linkType)
        return self.getLinkedPointsForLinks(linkColl)


    def getLinkedPointsForLinks(self, linkColl):
        if len(linkColl) > 0:
            rootKeys = [link.root for link in linkColl if link.root]
            roots = ndb.get_multi(rootKeys)
            linkedPoints = []            
                            
            for pointRoot in roots:
                if pointRoot:
                    linkedPoints = linkedPoints + [pointRoot.getCurrent()]
                else: # THIS SHOULD NEVER HAPPEN, BUT IT DID ONCE OR TWICE
                    logging.info('WARNING: Supporting point array for ' +
                                 self.url + ' contains pointer to missing root')

            # logging.info('ZPL' + str(zip(points, linkColl)))            
            for point, link in zip(linkedPoints, linkColl):
                point._linkInfo = link
                            
            return linkedPoints
        else:
            return None        
    
    @ndb.tasklet
    def getLinkedPoints_async(self, linkType, user):
        linkColl = self.getStructuredLinkCollection(linkType)
        if len(linkColl) > 0:
            rootKeys = [link.root for link in linkColl if link.root]
            
            linkedPoints = yield map(lambda x: getCurrent_async(x), 
                         (yield ndb.get_multi_async(rootKeys)))                        
            
            if user:
                linkedPoints = yield map(lambda x: x.addVote_async(user),linkedPoints) 
                                
            i = 0
            # this let met skip over link entries that do not have a root or do not match for some reason
            for point in linkedPoints:
                if linkColl[i].root == point.key.parent():                   
                    point._linkInfo = linkColl[i]
                i = i+1
                    
            raise ndb.Return(linkedPoints)
        else:
            raise ndb.Return(None)
        
         
    # gets both supporting and counter points, with their relevance
    def getAllLinkedPoints(self, user):
        supportingPoints = self.getLinkedPoints("supporting", user)
        counterPoints = self.getLinkedPoints("counter", user)
        
        if user: # add this user's relevance votes to the points
            # get all relevance votes with this as the parent point
            relevanceVotes = user.getRelevanceVotes(self)
            if relevanceVotes:
                self.addRelevanceVotes(relevanceVotes, supportingPoints, counterPoints)                
        return supportingPoints, counterPoints
        
    
    def addRelevanceVotes(self, relevanceVotes, supportingPoints, counterPoints):
        if relevanceVotes:
            relevanceVoteDict = dict((rVote.childPointRootKey, rVote) 
                for rVote in relevanceVotes)

            if supportingPoints:
                for p in supportingPoints:     
                    if p.key.parent() in relevanceVoteDict:
                        p._relevanceVote =relevanceVoteDict[p.key.parent()]                    
            if counterPoints:                
                for p in counterPoints:
                    if p.key.parent() in relevanceVoteDict:
                        p._relevanceVote =relevanceVoteDict[p.key.parent()]
    
        return supportingPoints, counterPoints
    
    # DATASTORE GET OF THE LAST CHANGE LINK POINTS BY LINK TYPE
    # THIS WILL GET THE VERSION OF THE LINKED POINTS AT THE TIME 
    #   THE LINK WAS CREATED
    def getLinkedPointsLastChange(self, linkType):
        linkColl = self.getStructuredLinkCollection(linkType)
        if len(linkColl) > 0:
            pointKeys = [link.version for link in linkColl if link.version]
            points = ndb.get_multi(pointKeys)
            return points
        else:
            return None   

    def addLink(self, linkRoot, linkCurrentVersion, linkType, voteCount, fRating):
        links = self.getStructuredLinkCollection(linkType)        
        if not voteCount:
            voteCount = 0
            
        if linkCurrentVersion:
            if linkRoot is None:
                raise WhysaurusException(
                    "Trying to add a new %s point but root was not supplied: %s" % (linkType, self.title))
            for link in links:
                if link.root == linkRoot.key:
                    raise WhysaurusException(
                        "That point is already a %s point of %s" % 
                            (linkType, self.title))
                elif link.version == linkCurrentVersion.key:
                    raise WhysaurusException(
                        "That point is already a %s point of %s" % 
                            (linkType, self.title))
                            
            linkCurrentVersion.isTop = False
            linkCurrentVersion.put()
            
            logging.info('Linking the new point. Have: %d, %d' % (voteCount, fRating))
            newLink = Link(
                root = linkRoot.key,
                version = linkCurrentVersion.key,
                voteCount = voteCount,
                fRating = fRating
            )
            linkCurrentVersion._linkInfo = newLink
            links = links + [newLink] if links else [newLink]      
            links = self.sortLinks(linkType, links)

            # Gene: Really, this needs to operate with the user that adds the link no?
            # (But right now that's updated as author already - if we change that we'll need to pass it.)
            root_user = linkCurrentVersion.authorURL
            if root_user:
                logging.info('Adding contributing user: %s -> %s' % (root_user, self.url))
                self.addContributingUser(root_user)
                self.put()

    def getChildPointRating(self, sp):
        return max(0, sp.upVotes - sp.downVotes + 1) * (sp._linkInfo.rating / 100.0)

    def getChildrenPointRating(self):
        """
        Looks one level down to get supporting and counter votes
        as influence.

        We disregard points with disagrees > agrees
        because stupid people adding bad arguments to the bottom
        shouldn't count against you.  If you have zero of both,
        we still give you +1 (times relevance) for that.

        We don't recurse below one level because the relevance
        of those arguments to the weighting one are uncertain.
        If arguments for a lower point are relevant to the top
        level, then they should be marshalled and added directly.

        WARNING: if you are ever tempted to add recursive weighting
        make sure you exclude cycles (a sub point linking to the same point
        higher up) to avoid infinite loop calculations
        """
        supportingPoints = self.getLinkedPoints('supporting', None) or []
        counterPoints = self.getLinkedPoints('counter', None) or []
        return int(round((sum([self.getChildPointRating(sp)
                               for sp in supportingPoints
                               if sp.upVotes >= sp.downVotes])
                          - (sum([self.getChildPointRating(cp)
                                  for cp in counterPoints
                                  if cp.upVotes >= cp.downVotes])))))

    def sortLinks(self, linkType=None, linksSeed=None):
        """
        Sorts links for supporting/counter link columns base on:
        * relevance -- anything less relevant should be lower. Even with high agrees
          the same people that clicked "agree" may have also voted it less relevant
        * Link's pointValue based on agrees and robustness

        With no arguments, it sorts both sides with the same list
        """
        sortedLinks = None
        linkTypes = [linkType]
        if linkType is None:
            linkTypes = ["counter", "supporting"]
            linksSeed = None
        for linkType in linkTypes:
            links = linksSeed or self.getStructuredLinkCollection(linkType)
            linkPoints = self.getLinkedPointsForLinks(links)
            # will sort on first item in tuple, then second...
            # adding lp._linkInfo at the end so it can be returned
            sortingList = sorted([(lp._linkInfo.rating, lp.pointValue(), lp._linkInfo)
                                  for lp in linkPoints],
                                 reverse=True)
            sortedLinks = [p[2] for p in sortingList]
            self.setStructuredLinkCollection(linkType, sortedLinks)
        return sortedLinks

    @ndb.tasklet
    def updateBacklinkedSorts(self, pointRoot, recurseUp=True):
        linkTypes = ["counter", "supporting"]
        for linkType in linkTypes:
            pointsAndRoots = pointRoot.getBacklinkPointRootPairs(linkType)
            for point,root in pointsAndRoots:
                point.sortLinks(linkType)
                point.put()
                if recurseUp:
                    # only go up one level, because further *sorting* is unaffected
                    # WARNING: if we DO recurse up, then must watch out for cycles!!
                    point.updateBacklinkedSorts(root, recurseUp=False)

    def removeLink(self, linkRoot, linkType):
        links = self.getStructuredLinkCollection(linkType)
        if linkRoot:
            for link in links:
                if link.root == linkRoot.key:
                    links.remove(link)
                    break;
            self.setStructuredLinkCollection(linkType, links)
        else:
            raise WhysaurusException(
                    "Trying to remove a %s point but root was not supplied: %s" % linkName, self.title)

    @ndb.transactional(xg=True)
    def transactionalUpdate(self, newPoint, theRoot, sources, user, pointsToLink):        
        self.put() # Save the old version
        if pointsToLink:
            for pointToLink in pointsToLink:
                if 'voteCount' in pointToLink:
                    logging.info('Linking the new point with Vote Count. Have: %d, %d' % \
                        ( pointToLink['voteCount'], pointToLink['fRating']))
                # addLink only adds to arrays
                newPoint.addLink(pointToLink['pointRoot'],
                                 pointToLink['pointCurrentVersion'],
                                 pointToLink['linkType'],
                                 pointToLink['voteCount'] if 'voteCount' in pointToLink else 0,
                                 pointToLink['fRating'] if 'fRating' in pointToLink else 0)
                # addLinkedPoint will add the backlink to the pointRoot and put
                pointToLink['pointRoot'].addLinkedPoint(newPoint.key.parent(),
                                                        pointToLink['linkType'])

        if sources:
            sourceKeys = newPoint.sources
            for source in sources:
                source.put()
                sourceKeys = sourceKeys + [source.key]
            newPoint.sources = sourceKeys
            
        # CONCURRENCY FIX
        # IN CASE A NEW CURRENT POINT HAS BEEN CREATED
        # LET'S TRY WITHOUT THIS
        """possiblyUpdatedRoot = theRoot.key.get()
        possiblyNewCurrent = possiblyUpdatedRoot.getCurrent()
        if (possiblyNewCurrent.key != self.key):
            logging.warning('Collision on the DB was detected.  Attempting to recover.')
            newPoint.version = possiblyNewCurrent.version + 1
            possiblyNewCurrent.current = False
            possiblyNewCurrent.put()"""

        newPoint.put()
        theRoot.current = newPoint.key
        theRoot.put()
        theRoot.setTop()
                
        deferred.defer(user.recordEditedPoint, theRoot.key, _transactional=ndb.in_transaction()) # Add to the user's edited list  
        return newPoint, theRoot

    # pointsToLink is a set of links of the new point we want to link
    def update( self, newTitle=None, newContent=None, newSummaryText=None, 
                pointsToLink=None, user=None, imageURL=None, imageAuthor=None,
                imageDescription=None, sourcesToAdd=None, sourceKeysToRemove=None):
        if user:
            theRoot = self.key.parent().get()
            newPoint = Point(parent=self.key.parent())  # All versions ancestors of the PointRoot

            newPoint.title = self.title if newTitle is None else newTitle
            newPoint.content = self.content if newContent is None else newContent

            if newSummaryText:
                newPoint.summaryText = newSummaryText if (len(
                    newSummaryText) != 250) else newSummaryText + '...'
            else:
                newPoint.summaryText = self.summaryText

            newPoint.authorName = user.name            
            newPoint.authorURL = user.url
            newPoint.creatorName = self.creatorName
            newPoint.creatorURL = self.creatorURL
            newPoint.supportingLinks = list(self.supportingLinks)
            newPoint.counterLinks = list(self.counterLinks)
                    
            newPoint.sources = self.sources
            keysToRemove = convertListToKeys(sourceKeysToRemove)
            if keysToRemove:
                for keyToRemove in keysToRemove:
                    for oldKey in newPoint.sources:
                        if oldKey == keyToRemove:
                            newPoint.sources.remove(oldKey)

            newPoint.version = self.version + 1
            newPoint.upVotes = self.upVotes # number of agrees
            newPoint.downVotes = self.downVotes # number of disagrees
            newPoint.voteTotal = self.voteTotal
            newPoint.imageURL = self.imageURL if imageURL is None else imageURL
            newPoint.imageDescription = self.imageDescription if imageDescription is None else imageDescription
            newPoint.imageAuthor = self.imageAuthor if imageAuthor is None else imageAuthor
            if newPoint.title != self.title:
                newPoint.url = theRoot.updateURL(newPoint.title)
            else:
                newPoint.url = self.url
            newPoint.current = True

            self.current = False

            newPoint, theRoot = self.transactionalUpdate(newPoint, theRoot, sourcesToAdd, user, pointsToLink)    

            # Not sure why this is needed: this should be getting handled by code already in addLink
            try:
                deferred.defer(Follow.createFollow, user.key, theRoot.key, "edited", _transactional=ndb.in_transaction())
            # If we are in transaction this is not allowed, but will be handled elsewhere
            except BadRequestError:
                pass

            if pointsToLink:
                # For now we only ever add a single linked point
                Point.addNotificationTask(
                    theRoot.key, 
                    user.key, 
                    4 if pointsToLink[0]['linkType'] == "supporting" else 5,
                    pointsToLink[0]['pointCurrentVersion'].title )
            else:
                Point.addNotificationTask(theRoot.key, user.key, 0) # "edited" notification

            # THIS COULD CHECK WHETHER IT IS NECESSARY TO UPDATE THE INDEX
            deferred.defer(newPoint.addToSearchIndexNew, _transactional=ndb.in_transaction() )

            return newPoint
        else:
            return None

    @classmethod
    @ndb.transactional(xg=True, retries=5)
    def transactionalAddSupportingPoint(cls, oldPointRoot, title, content, summaryText, user,
                            linkType, imageURL,imageAuthor,imageDescription,
                            sourcesURLs, sourcesNames, urlToUse):                             
         oldPointRoot = oldPointRoot.key.get() # re-get inside transaction for concurrency
         oldPoint = oldPointRoot.getCurrent()
         newLinkPoint, newLinkPointRoot = Point.create(
             title=title,
             content=content,
             summaryText=summaryText,
             user=user,
             backlink=oldPoint.key.parent(),
             linktype = linkType,
             imageURL=imageURL,
             imageAuthor=imageAuthor,
             imageDescription=imageDescription,
             sourceURLs=sourcesURLs,
             sourceNames=sourcesNames,
             urlToUse=urlToUse)
            
         newLinks = [{'pointRoot':newLinkPointRoot,
                     'pointCurrentVersion':newLinkPoint,
                     'linkType':linkType},
                     ]
         newPoint = oldPoint.update(
             pointsToLink=newLinks,                 
             user=user
         )            
         user.addRelevanceVote(
           oldPointRoot.key.urlsafe(), 
           newLinkPointRoot.key.urlsafe(), linkType, 100)
         return newPoint, newLinkPoint, newLinkPointRoot                                      

    @classmethod
    def addSupportingPoint(cls, oldPointRoot, title, content, summaryText, user,
                            linkType, imageURL,imageAuthor,imageDescription,
                            sourcesURLs, sourcesNames):                            
        newURL = makeURL(title) 
        try:
            newPoint, newLinkPoint, newLinkPointRoot = Point.transactionalAddSupportingPoint(
                oldPointRoot, title, content, summaryText, user,
                linkType, imageURL,imageAuthor,imageDescription,
                sourcesURLs, sourcesNames, newURL)            
        except TransactionFailedError as e:
            # DO NOT edit this error message carelessly, it is checked in (for example) point.js
            raise WhysaurusException("Could not add supporting point because someone else was editing this point at the same time.  Please try again.")
        Follow.createFollow(user.key, newLinkPointRoot.key, "created")
        Follow.createFollow(user.key, oldPointRoot.key, "edited")        
        return newPoint, newLinkPoint
    
    # ONLY REMOVES ONE SIDE OF THE LINK. USED BY UNLINK
    def removeLinkedPoint(self, unlinkPointRoot, linkType, user):
        if user:
            theRoot = self.key.parent().get()
            newPoint = Point(parent=theRoot.key)  # All versions ancestors of the caseRoot
            newPoint.authorName = user.name
            newPoint.authorURL = user.url

            newPoint.supportingLinks = list(self.supportingLinks)
            newPoint.counterLinks = list(self.counterLinks)
            
            newPoint.sources = list(self.sources)

            try:
                newPoint.removeLink(unlinkPointRoot, linkType)
            except Exception as e:
                logging.info(
                    'Could not remove supporting point from list: ' + str(e))
            newPoint.title = self.title
            newPoint.content = self.content
            newPoint.summaryText = self.summaryText
            newPoint.version = self.version + 1
            newPoint.upVotes = self.upVotes
            newPoint.downVotes = self.downVotes
            newPoint.voteTotal = self.voteTotal  
            newPoint.ribbonTotal = self.ribbonTotal
            newPoint.imageURL = self.imageURL
            newPoint.imageDescription = self.imageDescription
            newPoint.imageAuthor = self.imageAuthor
            newPoint.url = self.url
            newPoint.isTop = self.isTop
            self.current = False
            newPoint.current = True
            self.put()
            newPoint.put()
            theRoot.current = newPoint.key
            theRoot.put()
            
            Follow.createFollow(user.key, theRoot.key, "edited")
            
            Point.addNotificationTask(theRoot.key, user.key, 7 if linkType == "supporting" else 6)
            
            return newPoint
        else:
            return None

    def addContributingUser(self, userUrlContributed):
        if not userUrlContributed:
            logging.warning('addContributingUser: Invalid Contributing User!')
            return
        if userUrlContributed == self.creatorURL:
            logging.info('addContributingUser: Bypass For Author: %s' % userUrlContributed)
            return

        # Gene: Incrementally building for now - should switch to an error state once populated
        if self.usersContributed is None:
            self.usersContributed = []

        if userUrlContributed not in self.usersContributed:
            self.usersContributed = self.usersContributed + [userUrlContributed]
            self.put()
            logging.info('addContributingUser: %s -> %s' % (userUrlContributed, self.url))

    def getSources(self):
        if len(self.sources) > 0:
            sources = ndb.get_multi(self.sources)
            return sources
        else:
            return None
    
    @ndb.tasklet
    def getSources_async(self):
        if len(self.sources) > 0:
            sources = yield ndb.get_multi_async(self.sources)
            raise ndb.Return(sources)
        else:
            raise ndb.Return(None)

    def unlink(self, unlinkPointURL, linkType, user):
        unlinkPoint, unlinkPointRoot = Point.getCurrentByUrl(
            unlinkPointURL)
        newVersion = self.removeLinkedPoint(unlinkPointRoot, linkType, user)
        unlinkPointRoot.removeLinkedPoint(self.key.parent(), linkType)
        return newVersion

    @classmethod
    @ndb.tasklet
    def search(cls, user, searchTerms, excludeURL=None, linkType = ""):

        if searchTerms:
            index = search.Index('points')
            results = []
            searchResultDocs = index.search(searchTerms)
            
            if searchResultDocs:
                docIds = [resDoc.doc_id for resDoc in searchResultDocs]
                excludeList = []
                if excludeURL:
                    excludePoint, excludePointRoot = Point.getCurrentByUrl(
                        excludeURL)
                    if excludePointRoot:
                        excludeList = excludeList + [excludePointRoot.key.urlsafe()]
                        linkedPointRootKeys = excludePoint.getLinkedPointsRootKeys("supporting")
                        if linkedPointRootKeys:
                            for rootKey in linkedPointRootKeys:
                                excludeList = excludeList + [rootKey.urlsafe()]
                        
                        linkedPointRootKeys = excludePoint.getLinkedPointsRootKeys("counter")
                        if linkedPointRootKeys:
                            for rootKey in linkedPointRootKeys:
                                excludeList = excludeList + [rootKey.urlsafe()]
                                
                for key in excludeList:
                    try:
                        docIds.remove(key)
                    except ValueError:
                        pass 
                searchKeys = [ndb.Key(urlsafe=rootKey) for rootKey in docIds]
                logging.info("Search Keys %s" % str(searchKeys))          
                resultPoints = yield map(lambda x: getCurrent_async(x), (yield ndb.get_multi_async(searchKeys)))
                if user:
                    resultPoints = yield map(lambda x: x.addVote_async(user), resultPoints)                    
            else:
                resultPoints = None                
            raise ndb.Return(resultPoints)
        else:
            raise ndb.Return(None)
        
    def addToSearchIndexNew(self):
        index = search.Index(name='points')
        fields = [
            search.TextField(name='title', value=self.title),
            search.TextField(name='content', value=self.content),         
        ]
        d = search.Document(doc_id=self.key.parent().urlsafe(), fields=fields)
        index.put(d)
        
    # If old rel vote exists, replace its value, otherwise add a new value
    # into the value total
    def addRelevanceVote(self, oldRelVote, newRelVote):
        retVal = False, None, None
        if newRelVote: # should always be passed in
            links = self.getStructuredLinkCollection(newRelVote.linkType)
            ourLink = None
            for link in links:
                if link.root == newRelVote.childPointRootKey:
                    ourLink = link
                    break
            if ourLink:
                ourLink.updateRelevanceData(oldRelVote, newRelVote) 
                self.sortLinks(newRelVote.linkType, links)
                self.put()
                retVal = True, ourLink.rating, ourLink.voteCount
        return retVal        
        
    # This is used to fix database problems
    def addMissingBacklinks(self):
        if self.current == False:
            raise WhysaurusException('Add missing backlinks can only be invoked on current point')
        
        addedRoots = 0
        for linkType in ["supporting", "counter"]:
            links = self.getStructuredLinkCollection(linkType)            
            if links:
                for link in links:
                    # Every linked point in the link array of a current point 
                    #   should have backlinks in its root 
                    linkRoot = link.version.parent().get() # Get the root (parent) of the linked point                  
                    backlinks, archiveBacklinks = linkRoot.getBacklinkCollections(linkType)
                    if not self.key.parent() in backlinks:
                        linkRoot.addLinkedPoint(self.key.parent(), linkType)
                        addedRoots = addedRoots + 1
        return addedRoots
        
    @ndb.tasklet
    def addVote_async(self, user):
        if user:
            self._vote = yield user.getVoteValue_async(self.key.parent())
        raise ndb.Return(self)
        
    def addVote(self, user):
        if user:
            self._vote = user.getVoteValue(self.key.parent())
        return self

class PointRoot(ndb.Model):
    url = ndb.StringProperty()
    numCopies = ndb.IntegerProperty(indexed=False)
    current = ndb.KeyProperty(indexed=False)
    pointsSupportedByMe = ndb.KeyProperty(repeated=True, indexed=False)
    supportedArchiveForDelete = ndb.KeyProperty(repeated=True, indexed=False)
    pointsCounteredByMe = ndb.KeyProperty(repeated=True, indexed=False)
    counteredArchiveForDelete = ndb.KeyProperty(repeated=True, indexed=False)
    editorsPick = ndb.BooleanProperty(default=False)
    editorsPickSort = ndb.IntegerProperty(default=100000)
    viewCount = ndb.IntegerProperty()
    comments = ndb.KeyProperty(repeated=True, indexed=False)
    archivedComments = ndb.KeyProperty(repeated=True, indexed=False)    
    supportedCount = ndb.ComputedProperty(lambda e: len(e.pointsSupportedByMe))
    # A top point is not used as a support for other points, aka the root of an argument tree
    isTop = ndb.BooleanProperty(default=True)
    
    
    @classmethod
    def getByUrlsafe(cls, pointRootUrlSafe):
        return ndb.Key(urlsafe=pointRootUrlSafe).get()        


    @property
    def numComments(self):
        return len(self.comments) if self.comments else 0
        
    @property
    def numArchivedComments(self):
        return len(self.archivedComments) if self.archivedComments else 0
        
    def getCurrent(self):
        # if self.current:
        #     logging.info("RETURNING CURRENT point: %s" % self.current.urlsafe())
        return self.current.get()
        # else:
        #     logging.info("CURRENT UNAVAILABLE in %s" % self.url)
        # return Point.query(Point.current == True, ancestor=self.key).get()    
        
    def getBacklinkCollections(self, linkType):
        if linkType == 'supporting':
            return self.pointsSupportedByMe, self.supportedArchiveForDelete
        elif linkType == 'counter':
            return self.pointsCounteredByMe, self.counteredArchiveForDelete
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)
        
    
    def getBacklinkPointRootPairs(self, linkType):
        backlinkRootKeys, backlinksArchiveKeys = self.getBacklinkCollections(linkType)
        backlinkRoots = ndb.get_multi(backlinkRootKeys)
        currentKeys = []
        for root in backlinkRoots:
            if root:
                currentKeys = currentKeys + [root.current]
            else:
                logging.error("Bad link detected in Root: %s. " % self.url)                    
        currentPoints = ndb.get_multi(currentKeys)
        return zip(currentPoints, backlinkRoots)
    
    def getBacklinkPoints(self, linkType):
        return [a[0] for a in self.getBacklinkPointRootPairs(linkType)]

    # This is used to fix database problems
    def cleanEmptyLinks(self):
        numCleaned = 0
        allVersions = self.getAllVersions()
        for point in allVersions:
            cleaned = False
            for linkType in ["supporting", "counter"]:
                links = point.getStructuredLinkCollection(linkType)
                cleanLinks = [l for l in links if l.version is not None and l.root is not None]
                numCleaned = numCleaned + len(links) - len(cleanLinks)
                if len(links) != len(cleanLinks):
                    cleaned = True                
                    point.setStructuredLinkCollection(linkType, cleanLinks)
            if cleaned: 
                point.put()                
        return numCleaned, len(allVersions)        
        
    # This is used to fix database problems
    def removeDeadBacklinks(self):
        removedRoots = 0
        for linkType in ["supporting", "counter"]:
            linkPoints, archivedLinkPoints = \
                self.getBacklinkCollections(linkType)
            for linkRootKey in linkPoints:
                linkRoot = linkRootKey.get()
                logging.info('Got linkRoot for %s ' % str(linkRootKey))
                if not linkRoot:
                    self.removeBacklinkRaw(linkType, linkRootKey)
                    removedRoots = removedRoots + 1
                    continue
        if removedRoots > 0:
            self.put()
        return removedRoots
            
    # This is used to fix database problems
    def removeBacklinkRaw(self, linkType, linkPointRootKey):
        if linkType == 'supporting':
            self.pointsSupportedByMe.remove(linkPointRootKey)
        elif linkType == 'counter':
            self.pointsCounteredByMe.remove(linkPointRootKey)
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)  
        self.setTop()

    def setTop(self):
        if len(self.pointsSupportedByMe) + len(self.pointsCounteredByMe) == 0:
            self.isTop = True
            self.put()
            current = self.getCurrent()
            if current:
                current.isTop = True
                current.put()
        else:
            self.isTop = False
            self.put()
            current = self.getCurrent()
            if current:
                current.isTop = False
                current.put()         

    def getComments(self):
        return ndb.get_multi(self.comments)

    def getArchivedComments(self):
        return ndb.get_multi(self.archivedComments)
        
    def removeLinkedPoint(self, linkPointRootKey, linkType, archive=True):
        if linkType == 'supporting':
            try:
                self.pointsSupportedByMe.remove(linkPointRootKey)
            except ValueError:
                logging.error('Could not remove %s backlink in point %s' % \
                              (linkType, self.url))
                
            if archive and linkPointRootKey not in self.supportedArchiveForDelete:
                self.supportedArchiveForDelete = self.supportedArchiveForDelete + \
                [linkPointRootKey]
            self.put()
            
        elif linkType == 'counter':
            try:
                self.pointsCounteredByMe.remove(linkPointRootKey)
            except ValueError:
                logging.error('Could not remove %s backlink in point %s' % \
                              (linkType, self.url))
            if archive and linkPointRootKey not in self.supportedArchiveForDelete:
                self.counteredArchiveForDelete = self.counteredArchiveForDelete + \
                [linkPointRootKey]
            self.put()
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)
        self.setTop()


    def addLinkedPoint(self, linkPointRootKey, linkType):
        if linkType == 'supporting':
            if linkPointRootKey not in self.pointsSupportedByMe:
                self.pointsSupportedByMe = self.pointsSupportedByMe + \
                [linkPointRootKey]      
                self.isTop = False                          
                self.put()
        elif linkType == 'counter':
            if linkPointRootKey not in self.pointsCounteredByMe:
                self.pointsCounteredByMe = self.pointsCounteredByMe + \
                [linkPointRootKey]
                self.isTop = False                
                self.put()
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)

    def addViewCount(self):
        if not self.viewCount:
            self.viewCount = 1
        self.viewCount = self.viewCount + 1
        future = self.put_async()
        return future

    def getAllVersions(self):
        return Point.query(ancestor=self.key).fetch()

    @staticmethod
    def getEditorsPicks(user):
        editorsPicks = []
        pointsRootsQuery = PointRoot.gql("WHERE editorsPick = TRUE ORDER BY editorsPickSort ASC")
        pointRoots = pointsRootsQuery.fetch(50)
        for pointRoot in pointRoots:
            editorsPicks = editorsPicks + [pointRoot.getCurrent()]
        return editorsPicks
        
    @staticmethod
    @ndb.tasklet
    def getEditorsPicks_async(user):
        rootsQuery = PointRoot.gql("WHERE editorsPick = TRUE ORDER BY editorsPickSort ASC")
        resultPoints = yield map(lambda x: x.current.get_async(), (yield rootsQuery.fetch_async(50)))
        if user:
            resultPoints = yield map(
                lambda x: x.addVote_async(user), 
                resultPoints
            )
        raise ndb.Return(resultPoints)

    @staticmethod
    @ndb.tasklet
    def getRecentActivityAll_async(user):
        pointsQuery = Point.gql(
            "WHERE current = TRUE ORDER BY dateEdited DESC")
        resultPoints = None
        if user:
            resultPoints = yield map(lambda x: x.addVote_async(user), (yield pointsQuery.fetch_async(50)))
        else:
            resultPoints = yield pointsQuery.fetch_async(50)
        raise ndb.Return(resultPoints)

    @staticmethod
    @ndb.tasklet
    def getRecentCurrentPoints_async(user):
        pointsQuery = Point.gql(
            "WHERE current = TRUE AND isTop = TRUE ORDER BY dateEdited DESC")
        resultPoints = None
        if user:
            resultPoints = yield map(lambda x: x.addVote_async(user), (yield pointsQuery.fetch_async(50)))
        else:
            resultPoints = yield pointsQuery.fetch_async(50)
        raise ndb.Return(resultPoints)
                
    @staticmethod
    def getRecentCurrentPoints(user):
        pointsQuery = Point.gql(
            "WHERE current = TRUE AND isTop = TRUE ORDER BY dateEdited DESC")
        resultPoints = None
        if user:
            resultPoints =  map(lambda x: x.addVote(user), (pointsQuery.fetch(50)))
            logging.info('RP ' + str(resultPoints))
        else:
            resultPoints =  pointsQuery.fetch(50)
        return resultPoints
        
    @staticmethod
    def getTopRatedPoints(filterList = None):
        pointsQuery = Point.gql("WHERE current = TRUE ORDER BY voteTotal DESC")
        topPointsRaw = pointsQuery.fetch(50)
        topPoints = [] if filterList else topPointsRaw
        if filterList:
            for point in topPointsRaw:
                if not point in filterList:
                    topPoints = topPoints + [point]
        return topPoints    
  
    @staticmethod
    @ndb.tasklet        
    def getTopRatedPoints_async(user):
        pointsQuery = Point.gql("WHERE current = TRUE ORDER BY voteTotal DESC")
        resultPoints = None
        if user:
            resultPoints = yield map(lambda x: x.addVote_async(user), (yield pointsQuery.fetch_async(50)))
        else:
            resultPoints = yield pointsQuery.fetch_async(50)            
        raise ndb.Return(resultPoints)
    
    
    @staticmethod
    def getTopViewedPoints(user):
        rootsQuery = PointRoot.gql("ORDER BY viewCount DESC")        
        roots = rootsQuery.fetch(50)
        currentKeys = [root.current for root in roots]
        return ndb.get_multi(currentKeys)
        
    @staticmethod
    @ndb.tasklet    
    def getTopViewedPoints_async(user):
        rootsQuery = PointRoot.gql("ORDER BY viewCount DESC") 
            
        resultPoints = yield map(lambda x: x.current.get_async(), (yield rootsQuery.fetch_async(50)))
        if user:
            resultPoints = yield map(
                lambda x: x.addVote_async(user), 
                resultPoints
            )
        raise ndb.Return(resultPoints)

    # NOT USED CURRENTLY
    @staticmethod
    def getTopAwardPoints(user):       
        pointsQuery = Point.gql("WHERE current = TRUE ORDER BY ribbonTotal DESC")
        points =  pointsQuery.fetch(50)
        logging.info("GTAP Got %d points" % len(points))
        return points
        
    def delete(self, user):
        if not user.isAdmin:
            return False, 'Not authorized'

        # Combine the lists and blow away all reference to me
        for linkType in ["supporting", "counter"]:
            currentlyLinked, archiveLinked = self.getBacklinkCollections(linkType)
            allLinkedKeys = currentlyLinked + archiveLinked
            linkedPointRoots = ndb.get_multi(allLinkedKeys)
            if linkedPointRoots: # There might not be any linkpoints
                for linkedPointRoot in linkedPointRoots:
                    if not linkedPointRoot:
                        logging.info("There was a NONE %s root Key in %s" % (linkType, linkedPointRoots))
                        continue
                    v = linkedPointRoot.getAllVersions()
                    for linkedPointVersion in v:
                        links = linkedPointVersion.getStructuredLinkCollection(linkType)
                        writeVersion = False
                        for link in links:
                            if link.root == self.key:
                                links.remove(link)
                                linkedPointVersion.setStructuredLinkCollection(linkType, links)                                
                            writeVersion = True
                            
                        if writeVersion: linkedPointVersion.put()


        points = self.getAllVersions()
        for point in points:
            # img = PointImage.query(ancestor=point.key).get()
            # if img:
            #  img.key.delete()
            point.key.delete()
            
        for comment in self.comments:
            comment.delete()

        for comment in self.archivedComments:
            comment.delete()

        # TODO: Find the user that created and edited this, and delete REFS

        self.deleteFromSearchIndex()
        self.key.delete()

        return True, ''

        
    def deleteFromSearchIndex(self):
        doc_index = search.Index(name="points")
        doc_index.delete(self.key.urlsafe())

    def updateURL(self, newTitle):
        newURL = makeURL(newTitle)
        oldURL = self.url
        self.url = newURL
        # self.put()

        redirectURL = RedirectURL()
        redirectURL.fromURL = oldURL
        redirectURL.toURL = newURL
        redirectURL.put()
        # If there is already a redirector object going to this URL, update it
        RedirectURL.updateRedirects(oldURL, newURL)
        return newURL
    
    def addComment(self, comment):        
        if self.comments:
            if comment.parentComment:
                i = self.comments.index(comment.parentComment)
                if i == -1:
                    raise WhysaurusException("Parent comment key not found in comment list for this point")
                else:
                    self.comments.insert(i+1, comment.key)
            else:
                self.comments = [comment.key] + self.comments
        else:
            self.comments = [comment.key]
        self.put()

        cur = self.current.get()
        if cur:
            root_user = comment.userUrl
            if root_user:
                cur.addContributingUser(root_user)
        
    # shift this comment and all its childern into the archived array
    # return the number of comments archived
    def archiveComments(self, commentKeyUrlsafe):
        if self.comments:
            commentsArchived = 0
            mainCommentKey = ndb.Key(urlsafe=commentKeyUrlsafe)
            if self._archiveCommentKey(mainCommentKey):
                commentsArchived = 1
            else:
                raise WhysaurusException('Comment requested for archiving was not found in this point')
                
            # Archive his whole thread if it exists
            qry = Comment.query(ancestor=mainCommentKey)
            for key in qry.iter(keys_only=True):  
                if self._archiveCommentKey(key):              
                    commentsArchived = commentsArchived + 1

            if commentsArchived > 0:
                self.put()
                
            return commentsArchived
            
        else:
            raise WhysaurusException('No comments found in this point. Archive request should not have been sent')
        
    # shift one key between arrays. True if shifted
    def _archiveCommentKey(self, commentKey):       
        if commentKey in self.comments:
            idx = self.comments.index(commentKey)
            del self.comments[idx]
            if not self.archivedComments:
                self.archivedComments = []
            self.archivedComments.append(commentKey)
            return True
        else:
            return False            
        
    def updateEditorsPick(self, editorsPick, editorsPickSort):
        self.editorsPick = editorsPick
        self.editorsPickSort = editorsPickSort
        self.put()
        return True

    def populateCreatorUrl(self):
        pointCurrent = self.getCurrent()
        if pointCurrent is None:
            logging.warning('Bypassing Root With No Current Point: %s' % self.url)
            return False

        if pointCurrent.creatorURL is not None:
            # logging.info('Point Creator Already Populated: %s' % self.url)
            return False

        versionsOfThisPoint = Point.query(ancestor=self.key).order(Point.version)
        firstVersion = versionsOfThisPoint.get()

        pointCurrent.creatorURL = firstVersion.authorURL
        pointCurrent.creatorName = firstVersion.authorName

        logging.info('Populating Point Creator: %s -> %s' % (firstVersion.authorURL, self.url))

        authors = []
        # code for listing number of contributors
        for point in versionsOfThisPoint:
            thisAuthor = {"authorName": point.authorName, "authorURL": point.authorURL }
            if thisAuthor not in authors:
                authors.append(thisAuthor)
                pointCurrent.addContributingUser(point.authorURL)

        pointCurrent.put()
        return True

# A dummy class to create an entity group
# For large groups this will cause issues with sharding them across datastore nodes
# Eventually a BG task should be written to copy these out of the OutlineRoot
class OutlineRoot(ndb.Model):
    pass


# A reference to a single global featured point, which can be changed
class FeaturedPoint(ndb.Model):
    featuredPoint = ndb.KeyProperty() # A Point Root key
    
    @staticmethod
    def getFeatured():
        fpList = FeaturedPoint.query().fetch(1)
        return fpList[0] if fpList else None
    
    @staticmethod
    def setFeatured(featuredKey):
        currentFP = FeaturedPoint.getFeatured()
        if currentFP:
            currentFP.featuredPoint = featuredKey
            currentFP.put()
        else:
            newFP = FeaturedPoint(featuredPoint = featuredKey)
            newFP.put()
        return True
  
    @staticmethod
    def getFeaturedPoint():
        fp = FeaturedPoint.getFeatured()
        point = None  
        if fp:
            pointRoot = fp.featuredPoint.get()
            point = pointRoot.getCurrent() if pointRoot else None
        return point
