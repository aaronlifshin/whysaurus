from google.appengine.ext import ndb

class Document(ndb.Model):
    title = ndb.StringProperty(required=True) 
    content = ndb.StringProperty(required=True)
    
    @staticmethod
    def getAllForAssignment(assignment):
        return Document.query(ancestor=assignment.key).fetch()