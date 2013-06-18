import os
import logging


from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point

class AaronTask(AuthHandler):
    def get(self):
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
