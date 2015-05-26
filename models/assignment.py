from google.appengine.ext import ndb
from document import Document

class Assignment(ndb.Model):
    title = ndb.StringProperty(required=True)
    summary = ndb.TextProperty(required=True)    
    directions = ndb.TextProperty(required=True)
    teacherInstructions = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    edited = ndb.DateTimeProperty(auto_now=True)
        
    @staticmethod
    def addAssignment(title, summary, directions, teacherInstructions, documents):
        a = Assignment(title=title, summary=summary, teacherInstructions=teacherInstructions, directions=directions)
        a.put()
        
        for document in documents:
            d = Document(parent=a.key, title=document['title'], content=document['content'])
            d.put()
            
    def edit(self, title, summary, directions, teacherInstructions, newDocs):
        self.title = title
        self.summary = summary
        self.teacherInstructions = teacherInstructions
        self.directions = directions

        oldDocs = Document.getAllForAssignment(self)
        for d in oldDocs:
            d.key.delete()
                    
        for document in newDocs:
            d = Document(parent=self.key, title=document['title'], content=document['content'])
            d.put()
            
        self.put()
            
    @staticmethod
    def getAll():
        allAssignments = []
        for a in Assignment.query():
            allAssignments.append(a) 
        return allAssignments

    @staticmethod
    def getByURLSafe(urlsafe):
        return ndb.Key(urlsafe=urlsafe).get()
                
    @property
    def urlSafe(self):
        return self.key.urlsafe()