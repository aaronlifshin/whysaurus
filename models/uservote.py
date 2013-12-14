from google.appengine.ext import ndb

class UserVote(ndb.Model):
    pointRootKey = ndb.KeyProperty(required=True)
    value = ndb.IntegerProperty(required=True, indexed=False)  # 1, 0, -1
    ribbon = ndb.BooleanProperty(default=False, indexed=False)        

class RelevanceVote(ndb.Model):    
    parentPointRootKey = ndb.KeyProperty(required=True)
    childPointRootKey = ndb.KeyProperty(required=True) 
    linkType = ndb.StringProperty()       
    value = ndb.IntegerProperty(required=True, indexed=False)  # 1, 0, -1
    