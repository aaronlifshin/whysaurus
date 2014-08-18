from google.appengine.api import namespace_manager
from google.appengine.ext import ndb
from models.whysaurusexception import WhysaurusException
import re
import logging

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
        elif PrivateArea.exists(newName):
            raise WhysaurusException(
                    "Sorry, PrivateArea %s already exists. Please choose a different name." % newName)
        newArea = PrivateArea(name=newName, id=newName)
        newArea.put()
        
    @staticmethod
    def exists(areaName):
        previousNamespace = namespace_manager.get_namespace()
        
        if previousNamespace and previousNamespace != '':                
            namespace_manager.set_namespace('') # DEFAULT NAMESPACE
            
        query = PrivateArea.query(PrivateArea.name==areaName)
        pa = query.get()
        
        if previousNamespace and previousNamespace != '':                
            namespace_manager.set_namespace(previousNamespace)
        
        logging.info('++++++++++++' + str(pa) + 'AN: ' + areaName)
        if pa:
            return True
        else:
            return False

