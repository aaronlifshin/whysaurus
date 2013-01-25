import re
import logging

from google.appengine.ext import ndb
from google.appengine.api import search

import webapp2_extras.appengine.auth.models as auth_models

    

# ***************************************************************************************
#  POINT MANIPULATION FUNCTIONS
# ***************************************************************************************

class UserVote(ndb.Model):
  pointRootKey = ndb.KeyProperty(required=True)
  value = ndb.IntegerProperty(required=True) # 1, 0, -1

# class PointImage(ndb.Model):

    
class WhysaurusUser(auth_models.User):
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)
  # name = db.StringProperty(required=True)
  # profile_url = db.StringProperty(required=True)
  # access_token = db.StringProperty(required=True)
  admin = ndb.BooleanProperty(default=False)
  recentlyViewedRootKeys = ndb.KeyProperty(repeated=True)

  @property
  def userVotes(self):
    if not hasattr(self, "_userVotes"):
      votes = UserVote.query(ancestor=self.key)
      # votes = qry.run()
      self._userVotes = {}
      if votes:
        for vote in votes:
          self._userVotes[vote.pointRootKey] = vote
    return self._userVotes
  
  def addVote(self, point, voteValue, updatePoint=True):
    pointRootKey = point.key.parent()
    previousVoteValue = 0
    newVote = None
    if pointRootKey in self.userVotes: # Vote already exists. Update      
      previousVoteValue = self.userVotes[pointRootKey].value
      newVote = self.userVotes[pointRootKey]
      newVote.value = voteValue
    if not newVote: # Create a brand new one
      newVote = UserVote(
        pointRootKey= pointRootKey,
        value=voteValue,
        parent=self.key
        )
    newVote.put()

    if updatePoint:
      if previousVoteValue == 0 and voteValue == 1: # UPVOTE
        point.upVotes = point.upVotes + 1       
      if previousVoteValue == 0 and voteValue == -1: # DOWNVOTE   
        point.downVotes = point.downVotes + 1    
      if previousVoteValue == 1 and voteValue == 0: # CANCEL UPVOTE
        point.upVotes = point.upVotes - 1    
      if previousVoteValue == -1 and voteValue == 0: # CANCEL DOWNVOTE  
        point.downVotes = point.downVotes - 1    
      if previousVoteValue == -1 and voteValue == 1: # DOWN TO UP
        point.downVotes = point.downVotes - 1
        point.upVotes = point.upVotes + 1            
      if previousVoteValue == 1 and voteValue == -1: # UP TO DOWN
        point.downVotes = point.downVotes + 1
        point.upVotes = point.upVotes - 1
      point.voteTotal = point.upVotes - point.downVotes   
      point.put()

    return newVote
  
  def updateRecentlyViewed(self, pointRootKey):
    addedToList = False
    
    if not self.recentlyViewedRootKeys:
      self.recentlyViewedRootKeys = [pointRootKey]
      addedToList = True
 
    if pointRootKey in self.recentlyViewedRootKeys:
      self.recentlyViewedRootKeys.remove(pointRootKey)
      self.recentlyViewedRootKeys.insert(0,pointRootKey)     
    else:
      self.recentlyViewedRootKeys.insert(0,pointRootKey)
      addedToList = True 
       
    if len(self.recentlyViewedRootKeys) > 10:
      self.recentlyViewedRootKeys.pop()

    self.put()

    return addedToList

  def getRecentlyViewed(self, excludeList = None):
    recentlyViewedPoints = [] 
    keysToGet = self.recentlyViewedRootKeys
    if excludeList:
      for x in excludeList:
        try:
          keysToGet.remove(x)
        except ValueError:
          pass
    pointRoots = ndb.get_multi(keysToGet)  
    for pointRoot in pointRoots:
      if pointRoot:
        recentlyViewedPoints = recentlyViewedPoints + [pointRoot.getCurrent()]
    return recentlyViewedPoints
        
class PointRoot(ndb.Model):
  url = ndb.StringProperty()
  numCopies = ndb.IntegerProperty()
  pointsSupportedByMe = ndb.KeyProperty(repeated=True)
  editorsPick = ndb.BooleanProperty(default=False)
  viewCount = ndb.IntegerProperty()
  
  def getCurrent(self):
    return Point.query(Point.current == True, ancestor=self.key).get()
  
  def removeSupportedPoint(self, supportedPointKey):
    self.pointsSupportedByMe.remove(supportedPointKey)
    self.put()
  
  def addSupportedPoint(self, supportedPointRootKey):
    self.pointsSupportedByMe = self.pointsSupportedByMe + [supportedPointRootKey]
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
    pointsRootsQuery = PointRoot.gql("WHERE editorsPick = TRUE")
    pointRoots = pointsRootsQuery.fetch(100)
    for pointRoot in pointRoots:
      editorsPicks = editorsPicks + [pointRoot.getCurrent()]
    return editorsPicks
    
  @staticmethod
  def getRecentCurrentPoints():    
    pointsQuery = Point.gql("WHERE current = TRUE ORDER BY dateEdited DESC")
    return pointsQuery.fetch(50)

  def delete(self):
    if self.pointsSupportedByMe:
      supportedPointRoot = self.pointsSupportedByMe[0].get()
      supportedPoint = supportedPointRoot.getCurrent()
      return False, 'Cannot delete this point as it supports %d other points. \n Title of first supported point: %s' % (len(self.pointsSupportedByMe), supportedPoint.title)
    else:
      points = self.getAllVersions()
      for point in points:
        #img = PointImage.query(ancestor=point.key).get()
        #if img:
        #  img.key.delete()
          point.key.delete()
      self.key.delete()
      return True, ''
  


class Point(ndb.Model):
  """Models an individual Point with an author, content, date and version."""
  authorName = ndb.StringProperty()
  authorID = ndb.StringProperty()
  content = ndb.TextProperty()
  title = ndb.StringProperty()
  dateEdited = ndb.DateTimeProperty(auto_now_add=True)
  version = ndb.IntegerProperty()
  supportingPoints = ndb.KeyProperty(repeated=True)
  current = ndb.BooleanProperty()
  url = ndb.StringProperty()
  upVotes = ndb.IntegerProperty()
  downVotes = ndb.IntegerProperty()
  voteTotal = ndb.IntegerProperty()
  imageURL = ndb.StringProperty(default='');
  imageDescription = ndb.StringProperty(default='')
  imageAuthor = ndb.StringProperty(default='');
  
  @classmethod
  def getByKey(cls, pointKey):  
    return ndb.Key('Point', pointKey).get()
          
  @staticmethod
  def getCurrentByUrl(url):
    pointRootQuery = PointRoot.gql("WHERE url= :1", url)
    pointRoot = pointRootQuery.get()
    point = None
    if pointRoot:
      point = Point.query(Point.current == True, ancestor=pointRoot.key).get()
    if point:
      return point, pointRoot
    else:
      return (None, None)

  @classmethod		
  def getFullHistory(cls, url):
    pointRoot = PointRoot.query(PointRoot.url == url).get()
    if pointRoot:
      # Just most recent 50 for now
      points = Point.query(ancestor=pointRoot.key).order(-Point.version).fetch(50)
      # Image code left commented for when multiple images are added
      # images = PointImage.query(ancestor=pointRoot.key).fetch(50)
      retVal = []
      for point in points:
        supportingPoints = point.getSupportingPoints()
        # pointImages = [image for image in images if image.key.parent() == point.key]
        # image = None
        # if pointImages:
        #   image = pointImages[0]
        retVal.append({"point":point, "supportingPoints":supportingPoints}) #, "image":image})
      return retVal
    else:
      return None

  @staticmethod     
  def makeUrl(sourceStr):
    longURL = sourceStr.replace(" ","_")
    newUrl = re.sub('[\W]+','', longURL[0:64])
    # Check if it already exists
    pointRootQuery = PointRoot.gql("WHERE url= :1", newUrl)
    pointRoot = pointRootQuery.get()
    if pointRoot:
      pointRoot.numCopies = pointRoot.numCopies + 1
      newUrl = newUrl + str(pointRoot.numCopies)
      pointRoot.put()
    return newUrl
  
  @staticmethod
  def create(title, content, user, pointSupported = None, imageURL = None, imageAuthor = None, imageDescription = None):
    newUrl = Point.makeUrl(title)
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
  
  # newSupportingPoint is the key of the PointRoot of the supporting point
  def update(self, newTitle = None, newContent = None, newSupportingPoint=None, user = None,
             imageURL = None, imageAuthor = None, imageDescription = None):
    if user:
      newPoint = Point(parent=self.key.parent()) # All versions ancestors of the caseRoot

      if newTitle:
        newPoint.title = newTitle
      else:
        newPoint.title = self.title

      if newContent:
        newPoint.content = newContent
      else:
        newPoint.content = self.content

      newPoint.authorName = user.name      
      if newSupportingPoint:
        newPoint.supportingPoints = self.supportingPoints + [newSupportingPoint]
      else:		
        newPoint.supportingPoints = list(self.supportingPoints)
    
      newPoint.version = self.version + 1
      newPoint.url = self.url
      newPoint.upVotes = self.upVotes
      newPoint.downVotes = self.downVotes
      newPoint.voteTotal = self.voteTotal
      newPoint.current = True
      newPoint.imageURL = self.imageURL if imageURL is None else imageURL
      newPoint.imageDescription = self.imageDescription if imageDescription is None else imageDescription
      newPoint.imageAuthor = self.imageAuthor if imageAuthor is None else imageAuthor

      self.current = False
      newPoint.put()
      self.put()
      newPoint.addToSearchIndex()
      
      return newPoint
    else:
      return None
    
  # ONLY REMOVES ONE SIDE OF THE LINK. USED BY UNLINK
  def removeSupportingPoint(self, supportingPointToRemove, user):
    if user:
      newPoint = Point(parent=self.key.parent()) # All versions ancestors of the caseRoot
      newPoint.authorName = user.name
      newPoint.supportingPoints = list(self.supportingPoints)
      logging.info('SUP PO: ' + str(newPoint.supportingPoints))
      logging.info('TO REM: ' + str(supportingPointToRemove))
      newPoint.supportingPoints.remove(supportingPointToRemove.key)
      newPoint.title = self.title
      newPoint.content = self.content
      newPoint.version = self.version + 1
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
        supportingPoints = supportingPoints + [pointRoot.getCurrent()]
      return supportingPoints
    else:
      return None

  def unlink(self, supportingPointURL, user):
    supportingPoint, supportingPointRoot = Point.getCurrentByUrl(supportingPointURL)
    newVersion = self.removeSupportingPoint(supportingPointRoot, user)
    supportingPointRoot.removeSupportedPoint(self.key.parent())
    return newVersion
  
  @classmethod 
  def search(cls, searchTerms, excludeURL):
    
    if searchTerms:
      index = search.Index('points')
      results = []
      searchResultDocs = index.search(searchTerms)
      if searchResultDocs:
        excludeList = []
        if excludeURL:
          excludePoint, excludePointRoot = Point.getCurrentByUrl(excludeURL)
          if excludePoint:
            excludeList = excludeList + [excludePoint.url]
            supportingPoints = excludePoint.getSupportingPoints()
            for supportingPoint in supportingPoints:
              excludeList = excludeList + [supportingPoint.url]
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
    index = search.Index(name='points')
    fields = [
              search.TextField(name='title',value=self.title),
              search.AtomField(name='url',value=self.url),
              search.NumberField(name='voteTotal',value=self.voteTotal )
              ]
    d = search.Document(doc_id=self.url, fields=fields)
    index.add(d)

    
