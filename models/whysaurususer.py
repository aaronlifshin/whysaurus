from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models

from uservote import UserVote

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
            

    def updateRecentlyViewed(self, pointRootKey):
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

        self.put()

        return addedToList

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
