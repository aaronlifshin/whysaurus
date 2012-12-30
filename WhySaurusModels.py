import re
import logging

from google.appengine.ext import db
from google.appengine.api import users

# ***************************************************************************************
#  POINT MANIPULATION FUNCTIONS
# ***************************************************************************************

class UserVote(db.Model):
  userKey =  db.StringProperty(required=True)
  pointRootKey = db.StringProperty(required=True)
  value = db.IntegerProperty(required=True) # 1, 0, -1
  
class User(db.Model):
  id = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True)
  name = db.StringProperty(required=True)
  profile_url = db.StringProperty(required=True)
  access_token = db.StringProperty(required=True)
  admin = db.BooleanProperty()
  recentlyViewedRootKeys = db.StringListProperty()

  @property
  def userVotes(self):
    if not hasattr(self, "_userVotes"):
      qry = UserVote.gql("WHERE ANCESTOR IS :1", self)
      votes = qry.run()
      self._userVotes = {}
      if votes:
        for vote in votes:
          self._userVotes[vote.pointRootKey] = vote
    return self._userVotes
  
  def addVote(self, point, voteValue, updatePoint=True):
    pointRootKey = str(point.parent().key())
    previousVoteValue = 0
    newVote = None
    if pointRootKey in self.userVotes: # Vote already exists. Update      
      previousVoteValue = self.userVotes[pointRootKey].value
      newVote = self.userVotes[pointRootKey]
      newVote.value = voteValue
    if not newVote: # Create a brand new one
      newVote = UserVote(
        userKey=str(self.key()),
        pointRootKey= pointRootKey,
        value=voteValue,
        parent=self
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
    pointRoots = PointRoot.get(keysToGet)  
    for pointRoot in pointRoots:
      if pointRoot:
        recentlyViewedPoints = recentlyViewedPoints + [pointRoot.getCurrent()]
    return recentlyViewedPoints
        
class PointRoot(db.Model):
  url = db.StringProperty()
  numCopies = db.IntegerProperty()
  pointsSupportedByMe = db.ListProperty(db.Key)
  editorsPick = db.BooleanProperty()
  viewCount = db.IntegerProperty()
  
  def getCurrent(self):
    pointQuery = Point.gql("WHERE ANCESTOR IS :1 and current = TRUE", self)
    points = pointQuery.fetch(1)
    if points:
      return points[0]
    else:
      return None
  
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
    
  @staticmethod
  def getEditorsPicks():
    editorsPicks = []
    pointsRootsQuery = PointRoot.gql("WHERE editorsPick = TRUE")
    pointRoots = pointsRootsQuery.fetch(100)
    for pointRoot in pointRoots:
      editorsPicks = editorsPicks + [pointRoot.getCurrent()]
    return editorsPicks

class Point(db.Model):
  """Models an individual Point with an author, content, date and version."""
  authorName = db.StringProperty()
  authorID = db.StringProperty()
  content = db.TextProperty()
  title = db.StringProperty()
  dateEdited = db.DateTimeProperty(auto_now_add=True)
  version = db.IntegerProperty()
  supportingPoints = db.StringListProperty()
  current = db.BooleanProperty()
  url = db.StringProperty()
  upVotes = db.IntegerProperty()
  downVotes = db.IntegerProperty()
  voteTotal = db.IntegerProperty()
          
  @staticmethod
  def getCurrentByUrl(url):
    points = None
    pointRootQuery = PointRoot.gql("WHERE url= :1", url)
    pointRoot = pointRootQuery.get()
    if pointRoot:
      pointQuery = Point.gql("WHERE ANCESTOR IS :1 and current = TRUE", pointRoot)
      points = pointQuery.fetch(1)
    if points:
      return {"pointRoot":pointRoot, "point":points[0]} 
    else:
      return None

  @staticmethod		
  def getAllByUrl(url, orderByClause = ""):
    # TODO: FIND A WAY TO DO THIS WITHOUT TWO FETCHES.  FIRST IS NEEDED ONLY TO SET THE FETCH AMOUNT
    # 28/2/12 THIS IS ONLY USED AT POINT DELETE WHICH SHOULD NOT BE A COMMON OPERATION
    # THIS CAN BE DONE BY PASSING PARENT KEY
    pointRootQuery = PointRoot.gql("WHERE url= :1", url)
    pointRoot = pointRootQuery.get()	
    if pointRoot:
      pointQuery = Point.gql("WHERE ANCESTOR IS :1 "+ orderByClause, pointRoot)
      points = pointQuery.fetch(50) # Only 50 for now
      return points
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
  def create(title, content, user, pointSupported = None):
    newUrl = Point.makeUrl(title)
    pointRoot = PointRoot()
    pointRoot.url = newUrl
    pointRoot.numCopies = 0
    pointRoot.editorsPick = False
    pointRoot.viewCount = 1
    if pointSupported:
      pointRoot.pointsSupportedByMe = [pointSupported]
    pointRoot.put()
			
    point = Point(parent=pointRoot)
    point.title = title
    point.url = pointRoot.url			
    point.content = content
    point.authorID = user.id
    point.authorName = user.name
    point.version = 1
    point.current = True
    point.upVotes = 1
    point.downVotes = 0
    point.voteTotal = 1
    point.put()
    
    user.addVote(point, voteValue=1, updatePoint=False)
    user.updateRecentlyViewed(str(pointRoot.key()))
    
    return {"pointRoot":pointRoot, "point":point}
  
  # newSupportingPoint is the key of the PointRoot of the supporting point
  def update(self, newTitle = None, newContent = None, newSupportingPoint=None, user = None):
    if user:
      newPoint = Point(self.parent_key()) # All versions ancestors of the caseRoot

      if newTitle:
        newPoint.title = newTitle
      else:
        newPoint.title = self.title

      if newContent:
        newPoint.content = newContent
      else:
        newPoint.content = self.content

      newPoint.authorID = user.id
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
      self.current = False
      newPoint.put()
      self.put()
      return newPoint
    else:
      return None
    
  # ONLY REMOVES ONE SIDE OF THE LINK. USED BY UNLINK
  def removeSupportingPoint(self, supportingPointToRemove, user):
    if user:
      newPoint = Point(self.parent_key()) # All versions ancestors of the caseRoot
      newPoint.authorID = user.id
      newPoint.authorName = user.name
      newPoint.supportingPoints = list(self.supportingPoints)
      newPoint.supportingPoints.remove(supportingPointToRemove)
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
      supportingPointRoots = PointRoot.get(self.supportingPoints)
      supportingPoints = []
      for pointRoot in supportingPointRoots:
        supportingPoints = supportingPoints + [pointRoot.getCurrent()]
      return supportingPoints
    else:
      return None

  def unlink(self, supportingPointKey, user):
    supportingPointRoot = Point.get(supportingPointKey).parent()
    newVersion = self.removeSupportingPoint(str(supportingPointRoot.key()), user)
    supportingPointRoot.removeSupportedPoint(self.parent().key())
    return newVersion
