from google.appengine.api import namespace_manager
from google.appengine.ext import ndb
from models.whysaurusexception import WhysaurusException
from models.assignment import Assignment
from models.document import Document
import re
import logging

class PrivateArea(ndb.Model):
    name = ndb.StringProperty()
    displayName = ndb.StringProperty()
    
    @staticmethod
    def create(newName, newDisplayName):
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
        newArea = PrivateArea(name=newName, id=newName, displayName=newDisplayName)
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
    
    @staticmethod
    def getDisplayName(areaName):

        previousNamespace = namespace_manager.get_namespace()
        
        if previousNamespace and previousNamespace != '':                
            namespace_manager.set_namespace('') # DEFAULT NAMESPACE
        
        query = PrivateArea.query(PrivateArea.name==areaName)
        logging.info(query)
        pa = query.get()

        if previousNamespace and previousNamespace != '':                
            namespace_manager.set_namespace(previousNamespace)
        
        logging.info('++++++++++++ getDisplayName' + str(pa) + 'AN: ' + areaName)
        if pa:
            if pa.displayName is not None:
                return pa.displayName
            else:
                return areaName
        else:
            return ''
    
    def addAssignment(self, title, summary, directions, documents):
        a = Assignment(parent=self, title=title, summary=summary, directions=directions)
        a.put()
        
        for document in documents:
            d = Document(parent=a, title=document.title, content=document.content)
            d.put()

    
        
