from google.appengine.ext import ndb
from document import Document

class Assignment(ndb.Model):
    title = ndb.StringProperty(required=True)
    summary = ndb.TextProperty(required=True)    
    directions = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
        
    @staticmethod
    def addAssignment(title, summary, directions, documents):
        a = Assignment(title=title, summary=summary, directions=directions)
        a.put()
        
        for document in documents:
            d = Document(parent=a.key, title=document['title'], content=document['content'])
            d.put()
            
    @staticmethod
    def getAll():
        return Assignment.query()

    @staticmethod
    def getByURLSafe(urlsafe):
        return ndb.Key(urlsafe=urlsafe).get()
                
    @property
    def urlSafe(self):
        return self.key.urlsafe()