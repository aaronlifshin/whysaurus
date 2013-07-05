from google.appengine.ext import ndb

class UserVote(ndb.Model):
    pointRootKey = ndb.KeyProperty(required=True)
    value = ndb.IntegerProperty(required=True)  # 1, 0, -1
    ribbon = ndb.BooleanProperty(default=False)
    
