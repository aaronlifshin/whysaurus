from google.appengine.ext import ndb
from models.whysaurusexception import WhysaurusException
import re

class PrivateArea(ndb.Model):
    name = ndb.StringProperty()
    
    @staticmethod
    def create(newName):
        namespaceCheck = re.compile('[0-9A-Za-z._-]{0,100}')
        if not namespaceCheck.match(newName): 
            raise WhysaurusException(
                    "The only characters allowed are alphanumeric and . - _" )
        elif len(newName) > 100:
            raise WhysaurusException(
                    "PrivateArea name exceeds maximum length (100 characters)" )
        newArea = PrivateArea(name=newName, id=newName)
        newArea.put()
        