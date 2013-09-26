import datetime
from google.appengine.ext import ndb

class Follow(ndb.Model):
    user = ndb.KeyProperty()
    pointRoot = ndb.KeyProperty()
    reason = ndb.StringProperty()
    reasonDate = ndb.DateTimeProperty(auto_now_add=True)
    shouldFollow = ndb.BooleanProperty(default=True)

    @classmethod 
    def createFollow(cls, userKey, pointRootKey, reason):
        q = cls.query(ndb.AND(cls.user == userKey, cls.pointRoot == pointRootKey))     
        existingFollow =  q.fetch(1)
        f = None
        if existingFollow:
            pass # There is already a follow for this user and this point
        else: # Create a new follow
            f = Follow(user=userKey, pointRoot = pointRootKey, reason=reason)
            f.put()
        return f
    
            

    @classmethod
    def getActiveFollowsForPoint(cls, pointRootKey):
        q = cls.query(ndb.AND(cls.pointRoot == pointRootKey, cls.shouldFollow == True))     
        follows = q.fetch(100)
        return follows
    
    
        
        
    
