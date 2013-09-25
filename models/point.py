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

def convertListToKeys(urlsafeList):
    if urlsafeList:
        outList = []
        for u in urlsafeList:
            outList = outList + [ndb.Key(urlsafe=u)]
        return outList 
    else:
        return None
        
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

class Point(ndb.Model):
    """Models an individual Point with an author, content, date and version."""
    authorName = ndb.StringProperty()
    authorURL = ndb.StringProperty()
    content = ndb.TextProperty()
    summaryText = ndb.TextProperty(
    )  # This is Text not String because I do not want it indexed
    title = ndb.StringProperty()
    dateEdited = ndb.DateTimeProperty(auto_now_add=True)
    version = ndb.IntegerProperty(default=1)
    # supportingPoints = ndb.KeyProperty(repeated=True) # DEPRECATED
    supportingPointsRoots = ndb.KeyProperty(repeated=True)
    supportingPointsLastChange = ndb.KeyProperty(repeated=True)
    counterPointsRoots = ndb.KeyProperty(repeated=True)
    counterPointsLastChange = ndb.KeyProperty(repeated=True)
    sources = ndb.KeyProperty(repeated=True)
    current = ndb.BooleanProperty()
    url = ndb.StringProperty()
    upVotes = ndb.IntegerProperty(default=1)
    downVotes = ndb.IntegerProperty(default=0)
    voteTotal = ndb.IntegerProperty(default=1)
    ribbonTotal = ndb.IntegerProperty(default=0)
    imageURL = ndb.StringProperty(default='')
    summaryMediumImage = ImageUrl('SummaryMedium')
    summaryBigImage = ImageUrl('SummaryBig')
    fullPointImage = ImageUrl('FullPoint')
    imageDescription = ndb.StringProperty(default='')
    imageAuthor = ndb.StringProperty(default='')

    @property
    def linksRatio(self):
        sup = len(self.supportingPointsRoots)
        cou = len(self.counterPointsRoots)
        if sup == 0 and cou == 0:
            return 50
        elif cou == 0:
            return 80
        elif sup == 0:
            return 20
        else:
            rat1 = sup/float(sup + cou)
            if rat1 < .2:
                return 20
            elif rat1 > .8:
                return 80
            else:
                return math.floor(rat1*100) # Django widthratio requires integers
 
    @property
    def PSTdateEdited(self):
        return PST.convert(self.dateEdited)
    
    @property
    def reverseLinksRatio(self):
        return 100 - self.linksRatio
   
    @property
    def onlySupport(self):
        sup = len(self.supportingPointsRoots)
        cou = len(self.counterPointsRoots)
        return sup > 0 and cou == 0
    
    @property
    def onlyCounter(self):
        sup = len(self.supportingPointsRoots)
        cou = len(self.counterPointsRoots)
        return sup == 0 and cou > 0
      
    @classmethod
    def getByKey(cls, pointKey):
        return ndb.Key('Point', pointKey).get()

    @classmethod
    def addNotificationTask(cls, pointRootKey, userKey, notifyReason):
        t = Task(url='/addNotifications', 
                 params={'rootKey':pointRootKey.urlsafe(),
                         'userKey':userKey.urlsafe(),
                         'notifyReason': notifyReason})
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
                supportingPointsLastVersion = point.getLinkPointsLastChange("supporting")
                counterPointsLastVersion = point.getLinkPointsLastChange("counter")
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
        point.upVotes = 1
        point.downVotes = 0
        point.voteTotal = 1
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

        user.addVote(point, voteValue=1, updatePoint=False)
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
                pointRoot.pointsCounterredByMe = [backlink]
                
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
        return Point.transactionalCreateTree(dataForPointTree, user)

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
        rootCol, lastChangeCol = self.getLinkCollections(linkType)
        if lastChangeCol:
            return len(lastChangeCol)
        else:
            return 0

    def getLinkCollections(self,linkName):
        if linkName == 'supporting':
            return self.supportingPointsRoots, self.supportingPointsLastChange
        elif linkName == 'counter':
            return self.counterPointsRoots, self.counterPointsLastChange
        else:
            return None, None

    def setLinkCollections(self,linkName, rootCollection, versionCollection):
        if linkName == 'supporting':
            self.supportingPointsRoots = rootCollection
            self.supportingPointsLastChange = versionCollection
        elif linkName == 'counter':
            self.counterPointsRoots = rootCollection
            self.counterPointsLastChange = versionCollection
        else:
            return

    def addLink(self, linkRoot, linkCurrentVersion, linkName):
        rootList, versionList = self.getLinkCollections(linkName)
        if linkCurrentVersion:
            if linkRoot is None:
                raise WhysaurusException(
                    "Trying to add a new %s point but root was not supplied: %s" % (linkName, self.title))
            elif rootList and linkRoot.key in rootList:
                raise WhysaurusException(
                    "That point is already a %s point of %s" % (linkName, self.title))
            elif versionList and linkCurrentVersion.key in versionList:
                raise WhysaurusException(
                    "That point is already a %s point of %s" % (linkName, self.title))
            else:
                if rootList:
                    rootList = rootList + [linkRoot.key]
                else:
                    rootList = [linkRoot.key]
                logging.info("Adding to list: %s" % linkCurrentVersion.key)
                if versionList:
                    versionList = versionList + [linkCurrentVersion.key]
                else:
                    versionList = [linkCurrentVersion.key]
                self.setLinkCollections(linkName, rootList, versionList)

    def removeLink(self, linkRoot, linkName):
        rootList, versionList = self.getLinkCollections(linkName)
        if linkRoot:
            rootList.remove(linkRoot.key)
            for supPoint in versionList:
                logging.info('Comparing %s with %s' % (supPoint.parent(), linkRoot.key))
                if supPoint.parent() == linkRoot.key:
                    versionList.remove(supPoint)
                    break
            self.setLinkCollections(linkName, rootList, versionList)
        else:
            raise WhysaurusException(
                    "Trying to remove a %s point but root was not supplied: %s" % linkName, self.title)

    @ndb.transactional(xg=True)
    def transactionalUpdate(self, newPoint, theRoot, sources, user):
        self.put()
        if sources:
            sourceKeys = newPoint.sources
            for source in sources:
                source.put()
                sourceKeys = sourceKeys + [source.key]
            newPoint.sources = sourceKeys
        newPoint.put()
        logging.info('Setting new current in ROOT for URL \'%s\' to: %s' % (theRoot.url , newPoint.key.urlsafe()))
        theRoot.current = newPoint.key
        theRoot.put()
        user.recordEditedPoint(theRoot.key)        
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
            newPoint.supportingPointsRoots = list(self.supportingPointsRoots)
            newPoint.supportingPointsLastChange = list(self.supportingPointsLastChange)
            newPoint.counterPointsRoots = list(self.counterPointsRoots)
            newPoint.counterPointsLastChange = list(self.counterPointsLastChange)
            if pointsToLink:
                for pointToLink in pointsToLink:
                    logging.info('Point to link as %s. Version: %s' % \
                                 (pointToLink['linkType'], pointToLink['pointCurrentVersion']))
                    newPoint.addLink(pointToLink['pointRoot'],
                                     pointToLink['pointCurrentVersion'],
                                     pointToLink['linkType'])
                    pointToLink['pointRoot'].addLinkedPoint(newPoint.key.parent(),
                                                            pointToLink['linkType'])
                    
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

            newPoint, theRoot = self.transactionalUpdate(newPoint, theRoot, sourcesToAdd, user)
                    
            Follow.createFollow(user.key, theRoot.key, "edited")
            Point.addNotificationTask(theRoot.key, user.key, "edited")

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
            newPoint.supportingPointsLastChange = list(self.supportingPointsLastChange)
            newPoint.supportingPointsRoots = list(self.supportingPointsRoots)
            newPoint.counterPointsRoots = list(self.counterPointsRoots)
            newPoint.counterPointsLastChange = list(self.counterPointsLastChange)
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
            Point.addNotificationTask(theRoot.key, user.key, "unlinked a %s point from" % linkType)
            
            return newPoint
        else:
            return None

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
    
    def getSources(self):
        if len(self.sources) > 0:
            sources = ndb.get_multi(self.sources)
            return sources
        else:
            return None

    def getLinkPointsLastChange(self, linkType):
        linkRoots, linkLastChange = self.getLinkCollections(linkType)

        if linkLastChange and len(linkLastChange) > 0:
            return ndb.get_multi(linkLastChange)
        else:
            return None


    def getCounterPoints(self):
        if len(self.counterPointsRoots) > 0:
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

    def getLinkedPoints(self, linkType):
        if linkType == 'supporting':
            return self.getSupportingPoints()
        elif linkType == 'counter':
            return self.getCounterPoints()
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)

    def getLinkedPointsRootCollection(self, linkType):
        if linkType == 'supporting':
            return self.supportingPointsRoots
        elif linkType == 'counter':
            return self.counterPointsRoots
        else:
            raise WhysaurusException( "Unknown link type: \"%s\"" % linkType)

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
                        linkedPoints = excludePoint.getSupportingPoints()
                        if linkedPoints:
                            for point in linkedPoints:
                                excludeList = excludeList + [point.key.parent().urlsafe()]
                        linkedPoints = excludePoint.getCounterPoints()
                        if linkedPoints:
                            for point in linkedPoints:
                                excludeList = excludeList + [point.key.parent().urlsafe()]
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
                resultPoints = [root.getCurrent() for root in resultRoots]
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
        logging.info('NEW ADD TO SEARCH INDEX. DocId = %s ' % self.key.parent().urlsafe())
        d = search.Document(doc_id=self.key.parent().urlsafe(), fields=fields)
        index.put(d)
        
    # This is used to fix database problems
    def addMissingBacklinks(self):
        if self.current == False:
            raise WhysaurusException('Add missing backlinks can only be invoked on current point')
        
        addedRoots = 0
        for linkType in ["supporting", "counter"]:
            linkRoots, linkLastChange = self.getLinkCollections(linkType)            
            if linkLastChange:
                for pointKey in linkLastChange:
                    # 2. Every linked point in the link array of a current point 
                    #    should have backlinks in the root of the linked point
                    linkRoot = pointKey.parent().get()
                    backlinks, archiveBacklinks = linkRoot.getBacklinkCollections(linkType)
                    if not self.key.parent() in backlinks:
                        backlinks.add(self.key.parent())
                        linkRoot.addLinkedPoint(self.key.parent(), linkType)
                        addedRoots = addedRoots + 1
        return addedRoots


class PointRoot(ndb.Model):
    url = ndb.StringProperty()
    numCopies = ndb.IntegerProperty()
    current = ndb.KeyProperty()
    pointsSupportedByMe = ndb.KeyProperty(repeated=True)
    supportedArchiveForDelete = ndb.KeyProperty(repeated=True)
    pointsCounteredByMe = ndb.KeyProperty(repeated=True)
    counteredArchiveForDelete = ndb.KeyProperty(repeated=True)
    editorsPick = ndb.BooleanProperty(default=False)
    editorsPickSort = ndb.IntegerProperty(default=100000)
    viewCount = ndb.IntegerProperty()
    comments = ndb.KeyProperty(repeated=True)

    @classmethod
    def getByUrlsafe(cls, pointRootUrlSafe):
        return ndb.Key(urlsafe=pointRootUrlSafe).get()        

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
    def reconcileVersionArrays(self):
        removedRoots = 0
    
        pointVersionArray = self.getAllVersions()   
        for point in pointVersionArray:
            writePoint = False
            for linkType in ["supporting", "counter"]:
                rootColl, lastChangeColl = point.getLinkCollections(linkType)
                rootsToRemove = []
                lastChangeRoots = [p.parent() for p in lastChangeColl]
                for rootKey in rootColl:
                    if rootKey not in lastChangeRoots:
                        rootsToRemove = rootsToRemove + [rootKey]
                for rootKeyToRemove in rootsToRemove:
                    rootColl.remove(rootKeyToRemove)
                    point.setLinkCollections(linkType, rootColl, lastChangeColl)
                    removedRoots = removedRoots + 1
                    writePoint = True
            if writePoint:
                point.put()
        return removedRoots
                            
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
            self.pointsSupportedByMe.remove(linkPointRootKey)
            if archive and linkPointRootKey not in self.supportedArchiveForDelete:
                self.supportedArchiveForDelete = self.supportedArchiveForDelete + \
                [linkPointRootKey]
            self.put()
        elif linkType == 'counter':
            self.pointsCounteredByMe.remove(linkPointRootKey)
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
        self.put()

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
                        rootColl, versionColl = linkedPointVersion.getLinkCollections(linkType)
                        writeVersion = False
                        if self.key in rootColl:
                            rootColl.remove(self.key)
                            writeVersion = True
                        for link in versionColl:
                            if link.parent() == self.key:
                                versionColl.remove(link)
                            writeVersion = True
                        linkedPointVersion.setLinkCollections(linkType, rootColl, versionColl)
                        if writeVersion: linkedPointVersion.put()


        points = self.getAllVersions()
        for point in points:
            # img = PointImage.query(ancestor=point.key).get()
            # if img:
            #  img.key.delete()
            point.key.delete()
            
        for comment in self.comments:
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
    
# A dummy class to create an entity group
# For large groups this will cause issues with sharding them across datastore nodes
# Eventually a BG task should be written to copy these out of the OutlineRoot
class OutlineRoot(ndb.Model):
    pass

        