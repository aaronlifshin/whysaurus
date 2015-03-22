from google.appengine.ext import ndb
from document import Document

class Assignment(ndb.Model):
    title = ndb.StringProperty(required=True)
    summary = ndb.StringProperty(required=True)    
    directions = ndb.StringProperty(required=True)