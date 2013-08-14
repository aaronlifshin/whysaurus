import re

from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models

from whysaurusexception import WhysaurusException
from uservote import UserVote

class WhysaurusUser(auth_models.User):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty(default=None)
    numCopies = ndb.IntegerProperty(default=0)
    admin = ndb.BooleanProperty(default=False)
    recentlyViewedRootKeys = ndb.KeyProperty(repeated=True)
    createdPointRootKeys = ndb.KeyProperty(repeated=True)
    editedPointRootKeys = ndb.KeyProperty(repeated=True)
    websiteURL =  ndb.StringProperty()
    areasOfExpertise =  ndb.StringProperty()
    currentProfession =  ndb.StringProperty()
    bio =  ndb.StringProperty()
    # linkedInProfileLink = ndb.StringProperty()
    # facebookProfileLink =  ndb.StringProperty()
    # googleProfileLink =  ndb.StringProperty()
    # twitterProfileLink =  ndb.StringProperty()

    @property
    def createdCount(self):
        return len(self.createdPointRootKeys)
 
    @property
    def editedCount(self): 
        return len(self.editedPointRootKeys)
         
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
        if pointRootKey in self.userVotes:  # Vote already exists. Update
            previousVoteValue = self.userVotes[pointRootKey].value
            newVote = self.userVotes[pointRootKey]
            newVote.value = voteValue
        if not newVote:  # Create a brand new one
            newVote = UserVote(
                pointRootKey=pointRootKey,
                value=voteValue,
                parent=self.key
            )
        newVote.put()

        if updatePoint:
            if previousVoteValue == 0 and voteValue == 1:  # UPVOTE
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 0 and voteValue == -1:  # DOWNVOTE
                point.downVotes = point.downVotes + 1
            if previousVoteValue == 1 and voteValue == 0:  # CANCEL UPVOTE
                point.upVotes = point.upVotes - 1
            if previousVoteValue == -1 and voteValue == 0:  # CANCEL DOWNVOTE
                point.downVotes = point.downVotes - 1
            if previousVoteValue == -1 and voteValue == 1:  # DOWN TO UP
                point.downVotes = point.downVotes - 1
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 1 and voteValue == -1:  # UP TO DOWN
                point.downVotes = point.downVotes + 1
                point.upVotes = point.upVotes - 1
            point.voteTotal = point.upVotes - point.downVotes
            point.put()

        return newVote

    def setRibbon(self, point, ribbonValue, updatePoint=True):
        pointRootKey = point.key.parent()
        previousRibbon = False
        newVote = None
        if pointRootKey in self.userVotes:  # Vote already exists. Update
            previousRibbon = self.userVotes[pointRootKey].ribbon
            newVote = self.userVotes[pointRootKey]
            newVote.ribbon = ribbonValue
        if not newVote:  # Create a brand new one
            newVote = UserVote(
                pointRootKey=pointRootKey,
                value=0,
                ribbon=ribbonValue,
                parent=self.key
            )
        newVote.put() 
        if updatePoint:
            if not previousRibbon and ribbonValue:
                point.ribbonTotal = point.ribbonTotal + 1
                point.put()
            elif previousRibbon and not ribbonValue:
                point.ribbonTotal = point.ribbonTotal - 1
                point.put()
        return newVote
            

    def _updateRecentlyViewed(self, pointRootKey):
        addedToList = False

        if not self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys = [pointRootKey]
            addedToList = True

        if pointRootKey in self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys.remove(pointRootKey)
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
        else:
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
            addedToList = True

        if len(self.recentlyViewedRootKeys) > 10:
            self.recentlyViewedRootKeys.pop()
        
        return addedToList

    
    def updateRecentlyViewed(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)
        self.put()
        return self.recentlyViewedRootKeys
    
    def recordCreatedPoint(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)
        if not self.createdPointRootKeys:
            self.createdPointRootKeys = [pointRootKey]
        else:
            self.createdPointRootKeys.insert(0, pointRootKey)
        self.put()
        
    def recordEditedPoint(self, pointRootKey, write=True):
        if not self.editedPointRootKeys:
            self.editedPointRootKeys = [pointRootKey]
        else:
            if not pointRootKey in self.editedPointRootKeys:
                self.editedPointRootKeys.insert(0, pointRootKey)
            else:
                self.editedPointRootKeys.remove(pointRootKey)
                self.editedPointRootKeys.insert(0, pointRootKey)
        if write:
            self.put()
        return self.editedPointRootKeys


    def getRecentlyViewed(self, excludeList=None):
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
                recentlyViewedPoints = recentlyViewedPoints + [
                    pointRoot.getCurrent()]
        return recentlyViewedPoints
    
    def getCreated(self):
        createdPoints = []
        pointRoots = ndb.get_multi(self.createdPointRootKeys[0:10])
        for pointRoot in pointRoots:
            createdPoints = createdPoints + [pointRoot.getCurrent()]
        return createdPoints

    def getEdited(self):
        editedPoints = []
        pointRoots = ndb.get_multi(self.editedPointRootKeys[0:10])
        for pointRoot in pointRoots:
            editedPoints = editedPoints + [pointRoot.getCurrent()]
        return editedPoints
    
    def update(self, newName, newWebsiteURL, newUserAreas, newUserProfession, newUserBio):
        self.name = newName if newName.strip() != "" else None
        self.websiteURL =  newWebsiteURL if newWebsiteURL.strip() != "" else None
        self.areasOfExpertise = newUserAreas if newUserAreas.strip() != "" else None
        self.currentProfession = newUserProfession if newUserProfession.strip() != "" else None
        self.bio = newUserBio if newUserBio.strip() != "" else None
        self.put()
        
    @staticmethod
    def constructURL(name):
        userURL = name.replace(" ", "_")
        userURL = re.sub('[\W]+', '', userURL)
        # Check if it already exists
        userQuery = WhysaurusUser.gql("WHERE url= :1", userURL)
        existingUser = userQuery.get()
    
        if existingUser:
            # Existing URL notes how many URLs+number exist for that URL
            existingUser.numCopies = existingUser.numCopies + 1
            userURL = userURL + str(existingUser.numCopies)
            existingUser.put()
        return userURL
            
    @staticmethod
    def getByUrl(url):
        qry = WhysaurusUser.gql("WHERE url= :1", url)
        return qry.get()


    
