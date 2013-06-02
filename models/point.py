import logging

from google.appengine.ext import ndb
from google.appengine.api import search

from imageurl import ImageUrl
from whysaurusexception import WhysaurusException

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
    return newUrl

class Point(ndb.Model):
    """Models an individual Point with an author, content, date and version."""
    authorName = ndb.StringProperty()
    authorID = ndb.StringProperty()
    content = ndb.TextProperty()
    summaryText = ndb.TextProperty(
    )  # This is Text not String because I do not want it indexed
    title = ndb.StringProperty()
    dateEdited = ndb.DateTimeProperty(auto_now_add=True)
    version = ndb.IntegerProperty()
    supportingPoints = ndb.KeyProperty(repeated=True)
    current = ndb.BooleanProperty()
    url = ndb.StringProperty()
    upVotes = ndb.IntegerProperty()
    downVotes = ndb.IntegerProperty()
    voteTotal = ndb.IntegerProperty()
    imageURL = ndb.StringProperty(default='')
    summaryMediumImage = ImageUrl('SummaryMedium')
    summaryBigImage = ImageUrl('SummaryBig')
    fullPointImage = ImageUrl('FullPoint')
    imageDescription = ndb.StringProperty(default='')
    imageAuthor = ndb.StringProperty(default='')

    @classmethod
    def getByKey(cls, pointKey):
        return ndb.Key('Point', pointKey).get()

    @staticmethod
    def getCurrentByUrl(url):
        pointRootQuery = PointRoot.gql("WHERE url= :1", url)
        pointRoot = pointRootQuery.get()
        point = None
        if pointRoot:
            point = Point.query(
                Point.current == True, ancestor=pointRoot.key).get()
        if point:
            return point, pointRoot
        else:
            return (None, None)

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
                supportingPoints = point.getSupportingPoints()
                # pointImages = [image for image in images if image.key.parent() == point.key]
                # image = None
                # if pointImages:
                #   image = pointImages[0]
                retVal.append({
                              "point": point, "supportingPoints": supportingPoints})  # , "image":image})
            return retVal
        else:
            return None

    @staticmethod
    def create(title, content, summaryText, user, pointSupported=None, imageURL=None, imageAuthor=None, imageDescription=None):
        newUrl = makeURL(title)
        pointRoot = PointRoot()
        pointRoot.url = newUrl
        pointRoot.numCopies = 0
        pointRoot.editorsPick = False
        pointRoot.viewCount = 1
        if pointSupported:
            pointRoot.pointsSupportedByMe = [pointSupported]
        pointRoot.put()

        point = Point(parent=pointRoot.key)
        point.title = title
        point.url = pointRoot.url
        point.content = content
        point.summaryText = summaryText if (len(
            summaryText) != 250) else summaryText + '...'
        point.authorName = user.name
        point.version = 1
        point.current = True
        point.upVotes = 1
        point.downVotes = 0
        point.voteTotal = 1
        point.imageURL = imageURL
        point.imageDescription = imageDescription
        point.imageAuthor = imageAuthor
        point.put()
        point.addToSearchIndex()

        user.addVote(point, voteValue=1, updatePoint=False)
        user.updateRecentlyViewed(pointRoot.key)
        return point, pointRoot

    # newSupportingPoint is the PointRoot of the supporting point
    def update(
        self, newTitle=None, newContent=None, newSummaryText=None, newSupportingPoint=None, user=None,
            imageURL=None, imageAuthor=None, imageDescription=None):
        if user:
            theRoot = self.key.parent().get()
            newPoint = Point(parent=self.key.parent())  # All versions ancestors of the caseRoot

            if not newTitle is None:
                newPoint.title = newTitle
            else:
                newPoint.title = self.title

            if not newContent is None:
                newPoint.content = newContent
            else:
                newPoint.content = self.content

            if newSummaryText:
                newPoint.summaryText = newSummaryText if (len(
                    newSummaryText) != 250) else newSummaryText + '...'
            else:
                newPoint.summaryText = self.summaryText

            newPoint.authorName = user.name
            if newSupportingPoint:
                if newSupportingPoint.key in self.supportingPoints:
                    raise WhysaurusException(
                        "That point is already a supporting point of " + newPoint.title)
                else:
                    newPoint.supportingPoints = self.supportingPoints + \
                        [newSupportingPoint.key]
            else:
                newPoint.supportingPoints = list(self.supportingPoints)

            newPoint.version = self.version + 1
            newPoint.upVotes = self.upVotes
            newPoint.downVotes = self.downVotes
            newPoint.voteTotal = self.voteTotal
            newPoint.current = True
            newPoint.imageURL = self.imageURL if imageURL is None else imageURL
            newPoint.imageDescription = self.imageDescription if imageDescription is None else imageDescription
            newPoint.imageAuthor = self.imageAuthor if imageAuthor is None else imageAuthor

            self.current = False
            if newPoint.title != self.title:
                newPoint.url = theRoot.updateURL(newPoint.title)
            else:
                newPoint.url = self.url
            newPoint.put()
            self.put()
            if newSupportingPoint:
                newSupportingPoint.addSupportedPoint(newPoint.key.parent())

            # THIS NEEDS TO CHECK WHETHER IT IS NECESSARY TO UPDATE THE INDEX
            newPoint.addToSearchIndex()

            return newPoint
        else:
            return None

    # ONLY REMOVES ONE SIDE OF THE LINK. USED BY UNLINK
    def removeSupportingPoint(self, supportingPointToRemove, user):
        if user:
            newPoint = Point(
                parent=self.key.parent())  # All versions ancestors of the caseRoot
            newPoint.authorName = user.name
            newPoint.supportingPoints = list(self.supportingPoints)
            logging.info('SUP PO: ' + str(newPoint.supportingPoints))
            logging.info('TO REM: ' + str(supportingPointToRemove))
            try:
                newPoint.supportingPoints.remove(supportingPointToRemove.key)
            except Exception as e:
                logging.info(
                    'Could not remove supporting point from list: ' + str(e))
            newPoint.title = self.title
            newPoint.content = self.content
            newPoint.version = self.version + 1
            newPoint.upVotes = self.upVotes
            newPoint.downVotes = self.downVotes
            newPoint.voteTotal = self.voteTotal
            newPoint.url = self.url
            newPoint.current = True
            self.current = False
            newPoint.put()
            self.put()
            return newPoint
        else:
            return None

    def getSupportingPoints(self):
        if len(self.supportingPoints) > 0:
            supportingPointRoots = ndb.get_multi(self.supportingPoints)
            supportingPoints = []
            for pointRoot in supportingPointRoots:
                if pointRoot:
                    supportingPoints = supportingPoints + \
                        [pointRoot.getCurrent()]
                else:
                    logging.info('WARNING: Supporting point array for ' +
                                 self.url + ' contains pointer to missing root')
            return supportingPoints
        else:
            return None

    def unlink(self, supportingPointURL, user):
        supportingPoint, supportingPointRoot = Point.getCurrentByUrl(
            supportingPointURL)
        newVersion = self.removeSupportingPoint(supportingPointRoot, user)
        supportingPointRoot.removeSupportedPoint(self.key.parent())
        return newVersion

    @classmethod
    def search(cls, searchTerms, excludeURL=None):

        if searchTerms:
            index = search.Index('points')
            results = []
            searchResultDocs = index.search(searchTerms)
            if searchResultDocs:
                excludeList = []
                if excludeURL:
                    excludePoint, excludePointRoot = Point.getCurrentByUrl(
                        excludeURL)
                    if excludePoint:
                        excludeList = excludeList + [excludePoint.url]
                        supportingPoints = excludePoint.getSupportingPoints()
                        if supportingPoints:
                            for supportingPoint in supportingPoints:
                                excludeList = excludeList + \
                                    [supportingPoint.url]
                for doc in searchResultDocs:
                    newResult = {}
                    addResult = True
                    for field in doc.fields:
                        newResult[field.name] = field.value
                        if field.name == 'url' and field.value in excludeList:
                            addResult = False
                    if addResult:
                        results = results + [newResult]
            return results
        else:
            return None

    def addToSearchIndex(self):
        logging.info('ADDING TO SEARCH INDEX. URL = %s | MedIMG = %s '% (self.url, self.summaryMediumImage))
        index = search.Index(name='points')
        fields = [
            search.TextField(name='title', value=self.title),
            search.AtomField(name='url', value=self.url),
            search.NumberField(name='voteTotal', value=self.voteTotal),
            search.AtomField(name='summaryMediumImage', value=self.summaryMediumImage if self.imageURL else None)
        ]
        d = search.Document(doc_id=self.url, fields=fields)
        index.put(d)

class PointRoot(ndb.Model):
    url = ndb.StringProperty()
    numCopies = ndb.IntegerProperty()
    pointsSupportedByMe = ndb.KeyProperty(repeated=True)
    editorsPick = ndb.BooleanProperty(default=False)
    editorsPickSort = ndb.IntegerProperty(default=100000)
    viewCount = ndb.IntegerProperty()

    def getCurrent(self):
        return Point.query(Point.current == True, ancestor=self.key).get()

    def removeSupportedPoint(self, supportedPointKey):
        self.pointsSupportedByMe.remove(supportedPointKey)
        self.put()

    def addSupportedPoint(self, supportedPointRootKey):
        if supportedPointRootKey not in self.pointsSupportedByMe:
            self.pointsSupportedByMe = self.pointsSupportedByMe + \
                [supportedPointRootKey]
            self.put()

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
        return pointsQuery.fetch(10)

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


    def delete(self, user):
        if not user.admin:
            return False, 'Not authorized'

        if self.pointsSupportedByMe:
            for supportedPoint in self.pointsSupportedByMe:
                pointRoot = supportedPoint.get()
                if pointRoot:
                    point = pointRoot.getCurrent()
                    point.removeSupportingPoint(self, user)

        # MY SUPPORTING POINTS NO LONGER SUPPORT ME
        current = self.getCurrent()
        supportingPointRoots = ndb.get_multi(current.supportingPoints)
        for supportingPoint in supportingPointRoots:
            if supportingPoint:
                supportingPoint.removeSupportedPoint(self.key)

        points = self.getAllVersions()
        for point in points:
            # img = PointImage.query(ancestor=point.key).get()
            # if img:
            #  img.key.delete()
            point.key.delete()
        self.key.delete()
        return True, ''

    def updateURL(self, newTitle):
        newURL = makeURL(newTitle)
        oldURL = self.url
        self.url = newURL
        self.put()
        redirectURL = RedirectURL()
        redirectURL.fromURL = oldURL
        redirectURL.toURL = newURL
        redirectURL.put()
        # If there is already a redirector object going to this URL, update it
        RedirectURL.updateRedirects(oldURL, newURL)
        return newURL

