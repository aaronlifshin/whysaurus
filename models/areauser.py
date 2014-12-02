from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import Unique
from models.whysaurusexception import WhysaurusException
import logging


class AreaUser(ndb.Model):
    userKey = ndb.StringProperty(required=True)
    privateArea = ndb.StringProperty(required=True)
    uniqueAreaUserString = ndb.StringProperty()
    
    def __init__(self, *args, **kwargs):
        super(AreaUser, self).__init__(*args, **kwargs)
        self.uniqueAreaUserString = 'AreaUser.uniqueAreaUserString.%s:%s' % (self.userKey, self.privateArea)  
    
    def putUnique(self):
        success = Unique.create(self.uniqueAreaUserString)
        if success:    
            self.put()

    def deleteRelationship(self):
        success, existing = Unique.create_multi([self.uniqueAreaUserString])        
        Unique.delete_multi(existing)
        self.key.delete();
        
                