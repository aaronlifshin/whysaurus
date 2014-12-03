from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import Unique
from models.whysaurusexception import WhysaurusException
import logging


class AreaUser(ndb.Model):
    userKey = ndb.StringProperty(required=True)
    privateArea = ndb.StringProperty(required=True)
    
    def putUnique(self):
        success = Unique.create('AreaUser.uniqueAreaUserString.%s:%s' % (self.userKey, self.privateArea))
        if success:    
            self.put()

    def deleteRelationship(self):
        success, existing = Unique.create_multi(['AreaUser.uniqueAreaUserString.%s:%s' % (self.userKey, self.privateArea)])        
        Unique.delete_multi(existing)
        self.key.delete();
        
                