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
import re
import logging
import math

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api.taskqueue import Task


from imageurl import ImageUrl
from whysaurusexception import WhysaurusException
from redirecturl import RedirectURL
from source import Source
from timezones import PST
from follow import Follow
from uservote import RelevanceVote

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
  
def sortArrayByRating(links):      
    links.sort(key=lambda x: x.fRating if x.fRating is not None else 50, reverse=True)
    
class Link(ndb.Model):
    version = ndb.KeyProperty(indexed=False)
    root = ndb.KeyProperty(indexed=False)
    # rating = ndb.IntegerProperty(indexed=False)
    voteCount = ndb.IntegerProperty(indexed=False)
    fRating = ndb.FloatProperty(indexed=False)
    
    @property
    def rating(self):
        return int(round(self.fRating, 0)) if self.fRating else 0
        
    def updateRelevanceData(self, oldRelVote, newRelVote):
        startingRating = self.fRating if self.fRating else 0
        if oldRelVote:
            # this user has already voted
            newSum = startingRating * self.voteCount - oldRelVote.value + newRelVote.value
            logging.info("URD: newsum=" + str(newSum))
            self.fRating = newSum/self.voteCount                    
        else:
            newSum = startingRating * self.voteCount + newRelVote.value
            self.voteCount = self.voteCount + 1
            self.fRating = newSum/self.voteCount
        

class Point(ndb.Model):
    """Models an individual Point with an author, content, date and version."""
    authorName = ndb.StringProperty(indexed=False)
    authorURL = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    summaryText = ndb.TextProperty(indexed=False)  # This is Text not String because I do not want it indexed
    title = ndb.StringProperty(indexed=False)
    dateEdited = ndb.DateTimeProperty(auto_now_add=True) # Order by used
    version = ndb.IntegerProperty(default=1) # Order by used
    # supportingPoints = ndb.KeyProperty(repeated=True) # DEPRECATED
    
    supportingLinks = ndb.StructuredProperty(Link, repeated=True)
    supportingPointsRoots = ndb.KeyProperty(repeated=True)
    supportingPointsLastChange = ndb.KeyProperty(repeated=True)
    
    counterLinks = ndb.StructuredProperty(Link, repeated=True)    
    counterPointsRoots = ndb.KeyProperty(repeated=True)
    counterPointsLastChange = ndb.KeyProperty(repeated=True)
    
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
    _relevanceVote = None
    _linkInfo = None

    @property
    def numSupporting(self):
        return len(self.supportingLinks) if self.supportingLinks else 0
        
    @property
    def numCounter(self):
        return len(self.counterLinks) if self.counterLinks else 0

    @property
    def linksRatio(self):
        sup = self.numSupporting
        cou = self.numCounter
        if sup == 0 and cou == 0:
            return 50
        elif cou == 0:
            return 80
        elif sup == 0:
            return 20
        else:
            rat1 = sup/float(sup + cou)
            return math.floor(rat1*100) # Django widthratio requires integers
 
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
    def relevanceVoteCount(self):
        return 0 if self._linkInfo is None else self._linkInfo.voteCount
        
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
        t.add(queue_name="notifications")
        
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
                            imageDescription=None, sourceURLs=None, sourceNames=None):
        pointRoot.put()
        point = Point(parent=pointRoot.key)
        point.title = title
        point.url = pointRoot.url
        point.content = content
        point.summaryText = summaryText if (len(
            summaryText) != 250) else summaryText + '...'
        point.authorName = user.name
        point.authorURL = user.url
        point.version = 1
        point.current = True
        point.upVotes = 0
        point.downVotes = 0
        point.voteTotal = 0
        point.imageURL = imageURL
        point.imageDescription = imageDescription
        point.imageAuthor = imageAuthor
        point.put() 
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
        pointRoot.put()

        # No automatic agreement
        # user.addVote(point, voteValue=1, updatePoint=False)
        user.recordCreatedPoint(pointRoot.key)
        
        return point, pointRoot

    @staticmethod
    def create(title, content, summaryText, user, backlink=None, linktype="",
               imageURL=None, imageAuthor=None, imageDescription=None, 
               sourceURLs=None, sourceNames=None):
        newUrl = makeURL(title)
        pointRoot = PointRoot()
        pointRoot.url = newUrl
        pointRoot.numCopies = 0
        pointRoot.editorsPick = False
        pointRoot.viewCount = 1
        if backlink:
            if linktype == 'supporting':
                pointRoot.pointsSupportedByMe = [backlink]
            elif linktype == 'counter':
                pointRoot.pointsCounteredByMe = [backlink]
                
        createdPoint, createdPointRoot = Point.transactionalCreate(
                            pointRoot,title, content, summaryText, user,
                            imageURL, imageAuthor, imageDescription, 
                            sourceURLs, sourceNames )
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
            
        
        
    
    # RETURN BOTH LINK COLLECTIONS FOR SUPPLIED LINK TYPE
    # ONE LAST TIME FOR UPDATE TO NEw DB StrucTURE
    def getLinkCollections(self,linkType):
        if linkType == 'supporting':
            return self.supportingPointsRoots, self.supportingPointsLastChange
        elif linkType == 'counter':
            return self.counterPointsRoots, self.counterPointsLastChange
        else:
            return None, None   
        
    # SET THE LINK COLLECTION BY LINK TYPE
    """ 
    def setLinkCollections(self,linkType, rootCollection, versionCollection):
        if linkType == 'supporting':
            self.supportingPointsRoots = rootCollection
            self.supportingPointsLastChange = versionCollection
        elif linkType == 'counter':
            self.counterPointsRoots = rootCollection
            self.counterPointsLastChange = versionCollection
        else:
            return            

    # DATASTORE GET OF THE CURRENT VERSION OF THE LINKED POINT
    #   GOES THROUGH THE ROOT TO GET THE CURRENT POINT
    def getCounterPoints(self):
        if len(self.counterLinks) > 0:
            roots = [link.root for link in self.counterLinks]
            counterPointsRoots = ndb.get_multi(self.counterPointsRoots)
            counterPoints = []
            for pointRoot in counterPointsRoots:
                if pointRoot:
                    counterPoints = counterPoints + \
                        [pointRoot.getCurrent()]
                else:
                    logging.info('WARNING: Counter point array for ' +
                                 self.url + ' contains pointer to missing root')
            return counterPoints
        else:
            return None
            
    # DATASTORE GET OF THE CURRENT VERSION OF THE LINKED POINT
    #   GOES THROUGH THE ROOT TO GET THE CURRENT POINT
    def getSupportingPoints(self):
        if len(self.supportingPointsRoots) > 0:
            supportingPointsRoots = ndb.get_multi(self.supportingPointsRoots)
            supportingPoints = []
            for pointRoot in supportingPointsRoots:
                if pointRoot:
                    supportingPoints = supportingPoints + \
                        [pointRoot.getCurrent()]
                else:
                    logging.info('WARNING: Supporting point array for ' +
                                 self.url + ' contains pointer to missing root')
            return supportingPoints
        else:
            return None
    """

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
    
    # gets both supporting and counter points, with their relevance
    def getAllLinkedPoints(self, user):
        supportingPoints = self.getLinkedPoints("supporting", user)
        counterPoints = self.getLinkedPoints("counter", user)
        
        if user: # add this user's relevance votes to the points
            # get all relevance votes with this as the parent point
            relevanceVotes = user.getRelevanceVotes(self)
            if relevanceVotes:
                relevanceVoteDict = dict((rVote.childPointRootKey, rVote) 
                    for rVote in relevanceVotes)
                # logging.info('RVD: ' + str(relevanceVoteDict))
        
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

    def addLink(self, linkRoot, linkCurrentVersion, linkType):
        links = self.getStructuredLinkCollection(linkType)        
        
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
            newLink = Link(
                root = linkRoot.key,
                version = linkCurrentVersion.key,
                voteCount = 0
            )
            
            links = links + [newLink] if links else [newLink]      
            sortArrayByRating(links)                  
            self.setStructuredLinkCollection(linkType, links)

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
                # addLink only adds to arrays
                newPoint.addLink(pointToLink['pointRoot'],
                                 pointToLink['pointCurrentVersion'],
                                 pointToLink['linkType'])
                # addLinkedPoint will add the backlink to the pointRoot and put
                pointToLink['pointRoot'].addLinkedPoint(newPoint.key.parent(),
                                                        pointToLink['linkType'])
        if sources:
            sourceKeys = newPoint.sources
            for source in sources:
                source.put()
                sourceKeys = sourceKeys + [source.key]
            newPoint.sources = sourceKeys
        newPoint.put()
        theRoot.current = newPoint.key
        theRoot.put()
        user.recordEditedPoint(theRoot.key) # Add to the user's edited list    
        return newPoint, theRoot


    # newSupportingPoint is the PointRoot of the supporting point
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
            
            # TO REMOVE -- - 
            newPoint.supportingPointsRoots = list(self.supportingPointsRoots)
            newPoint.supportingPointsLastChange = list(self.supportingPointsLastChange)
            newPoint.counterPointsRoots = list(self.counterPointsRoots)
            newPoint.counterPointsLastChange = list(self.counterPointsLastChange)
            # END TO REMOVE - - - - 
            
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
            newPoint.upVotes = self.upVotes
            newPoint.downVotes = self.downVotes
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
                    
            Follow.createFollow(user.key, theRoot.key, "edited")
            if pointsToLink:
                # For now we only ever add a single linked point
                Point.addNotificationTask(
                    theRoot.key, 
                    user.key, 
                    4 if pointsToLink[0]['linkType'] == "supporting" else 5,
                    pointsToLink[0]['pointCurrentVersion'].title )
            else:
                Point.addNotificationTask(theRoot.key, user.key, 0) # "edited" notification

            # THIS NEEDS TO CHECK WHETHER IT IS NECESSARY TO UPDATE THE INDEX
            newPoint.addToSearchIndexNew()

            return newPoint
        else:
            return None

    # ONLY REMOVES ONE SIDE OF THE LINK. USED BY UNLINK
    def removeLinkedPoint(self, unlinkPointRoot, linkType, user):
        if user:
            theRoot = self.key.parent().get()
            newPoint = Point(parent=theRoot.key)  # All versions ancestors of the caseRoot
            newPoint.authorName = user.name
            newPoint.authorURL = user.url
            
            # TO REMOVE - - - - 
            newPoint.supportingPointsLastChange = list(self.supportingPointsLastChange)
            newPoint.supportingPointsRoots = list(self.supportingPointsRoots)
            newPoint.counterPointsRoots = list(self.counterPointsRoots)
            newPoint.counterPointsLastChange = list(self.counterPointsLastChange)
            # END TO REMOVE - - - - - 
            
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
            self.current = False
            newPoint.current = True
            self.put()
            newPoint.put()
            theRoot.current = newPoint.key
            theRoot.put()
            
            Follow.createFollow(user.key, theRoot.key, "edited")
            # 
            Point.addNotificationTask(theRoot.key, user.key, 6 if linkType == "supporting" else 7)
            
            return newPoint
        else:
            return None
    
    def getSources(self):
        if len(self.sources) > 0:
            sources = ndb.get_multi(self.sources)
            return sources
        else:
            return None

    def unlink(self, unlinkPointURL, linkType, user):
        unlinkPoint, unlinkPointRoot = Point.getCurrentByUrl(
            unlinkPointURL)
        newVersion = self.removeLinkedPoint(unlinkPointRoot, linkType, user)
        unlinkPointRoot.removeLinkedPoint(self.key.parent(), linkType)
        return newVersion

    @classmethod
    def search(cls, searchTerms, excludeURL=None, linkType = ""):

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
                resultRoots = ndb.get_multi(searchKeys)
                logging.info("Search Keys %s" % str(searchKeys))
                """
                for docId in docIds:
                    newResult = {}
                    addResult = True
                    for field in doc.fields:
                        newResult[field.name] = field.value
                        if field.name == 'url' and field.value in excludeList:
                            addResult = False
                    if addResult:
                        results = results + [newResult]
                """
                cleanRoots = filter(None, resultRoots)
                resultPoints = [root.getCurrent() for root in cleanRoots]
            else:
                resultPoints = None                
            return resultPoints
        else:
            return None
        
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
                sortArrayByRating(links)                               
                self.put()
                retVal = True, ourLink.rating, ourLink.voteCount
        return retVal        
        
    # This is used to fix database problems
    def addMissingBacklinks(self):
        if self.current == False:
            raise WhysaurusException('Add missing backlinks can only be invoked on current point')
        
        addedRoots = 0
        for linkType in ["supporting", "counter"]:
            # OLD Dzb STRUCTURE
            # linkRoots, linkLastChange = self.getLinkCollections(linkType)
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
    supportedCount = ndb.ComputedProperty(lambda e: len(e.pointsSupportedByMe))
    
    
    @classmethod
    def getByUrlsafe(cls, pointRootUrlSafe):
        return ndb.Key(urlsafe=pointRootUrlSafe).get()        


    @property
    def numComments(self):
        return len(comments) if comments else 0
        
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
        
    
    def getBacklinkPoints(self, linkType):
        backlinkRootKeys, backlinksArchiveKeys = self.getBacklinkCollections(linkType)
        backlinkRoots = ndb.get_multi(backlinkRootKeys)
        currentKeys = []
        for root in backlinkRoots:
            if root:
                currentKeys = currentKeys + [root.current]
            else:
                logging.error("Bad link detected in Root: %s. " % self.url)                    
        currentPoints = ndb.get_multi(currentKeys)
        return currentPoints
    
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
    
    def getComments(self):
        return ndb.get_multi(self.comments)

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


    def addLinkedPoint(self, linkPointRootKey, linkType):
        if linkType == 'supporting':
            if linkPointRootKey not in self.pointsSupportedByMe:
                self.pointsSupportedByMe = self.pointsSupportedByMe + \
                [linkPointRootKey]
                self.put()
        elif linkType == 'counter':
            if linkPointRootKey not in self.pointsCounteredByMe:
                self.pointsCounteredByMe = self.pointsCounteredByMe + \
                [linkPointRootKey]
                self.put()
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)


    def addViewCount(self):
        if not self.viewCount:
            self.viewCount = 1
        self.viewCount = self.viewCount + 1
        self.put_async()

    def getAllVersions(self):
        return Point.query(ancestor=self.key).fetch()

    @staticmethod
    def getEditorsPicks():
        editorsPicks = []
        pointsRootsQuery = PointRoot.gql("WHERE editorsPick = TRUE ORDER BY editorsPickSort ASC")
        pointRoots = pointsRootsQuery.fetch(100)
        for pointRoot in pointRoots:
            editorsPicks = editorsPicks + [pointRoot.getCurrent()]
        return editorsPicks

    @staticmethod
    def getRecentCurrentPoints():
        pointsQuery = Point.gql(
            "WHERE current = TRUE ORDER BY dateEdited DESC")
        return pointsQuery.fetch(50)

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
    def getTopAwardPoints():       
        pointsQuery = Point.gql("WHERE current = TRUE ORDER BY ribbonTotal DESC")
        points =  pointsQuery.fetch(50)
        logging.info("GTAP Got %d points" % len(points))
        return points

    @staticmethod
    def getTopViewedPoints():
        rootsQuery = PointRoot.gql("ORDER BY viewCount DESC")        
        roots = rootsQuery.fetch(50)
        currentKeys = [root.current for root in roots]
        return ndb.get_multi(currentKeys)

    def delete(self, user):
        if not user.admin:
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
                        # rootColl, versionColl = linkedPointVersion.getLinkCollections(linkType)
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
            comment.key.delete()

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
        
    def updateEditorsPick(self, editorsPick, editorsPickSort):
        self.editorsPick = editorsPick
        self.editorsPickSort = editorsPickSort
        self.put()
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

        