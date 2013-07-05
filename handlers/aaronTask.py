import os
import logging


from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from google.appengine.api import search



class AaronTask(AuthHandler):
    def get(self):
        bigMessage = []
        docIndex = search.Index(name="points")
        docIds = [d.doc_id for d in docIndex.get_range(limit=200, ids_only=True)]
        for docId in docIds:
            pointRoot = None
            try:
                pointRoot = ndb.Key(urlsafe=docId).get()
            except Exception as e:
                logging.info(
                    'Could not retrieve from doc ID %s. Error was: %s' % (docId, str(e)))
            if pointRoot:
                bigMessage.append("Found %s" % pointRoot.url)
            else:
                docIndex.delete(docId)
                bigMessage.append("Deleted %s" % docId)
        template_values = { 'message': bigMessage }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))               

        
        """
        REDO THE SEARCH INDEX SO THAT THE DOCID IS THE URLSAFE OF THE POINTROOT
        query = PointRoot.query()
        bigMessage = []
        i = 0
        doc_index = search.Index(name="points")

        for pointRoot in query.iter():                     
            doc_index.delete(pointRoot.url)
            bigMessage.append('Removing %s' % pointRoot.url)
            pointRoot.getCurrent().addToSearchIndexNew()
            bigMessage.append('Added %s' % pointRoot.url)
            i = i + 1

        bigMessage.append("Insertions made: %d" % i)

        template_values = {
            'message': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        
            
        MAKE ALL ROOTS HAVE A CURRENT
        
        query = PointRoot.query()
        i = 0
        for pointRoot in query.iter():            
            point = Point.query(Point.current == True, ancestor=pointRoot.key).get()
            pointRoot.current = point.key
            pointRoot.put()
            i = i+1
          
        template_values = {
            'message': "Edits made: %d" % i
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        """