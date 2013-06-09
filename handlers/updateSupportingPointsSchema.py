import os
import logging


from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point

class UpdateSupportingPointsSchema(AuthHandler):
    def get(self):
        query = Point.query()
        i = 0
        for point in query.iter():
            if point.supportingPoints:
                for pointKey in point.supportingPoints:
                    point.supportingPointsRoots.append(pointKey)
                point.supportingPoints = []
                for rootKey in point.supportingPointsRoots:
                    root = rootKey.get()
                    if root:
                        pointVer = root.getCurrent()
                        point.supportingPointsLastChange.append(pointVer.key)
                    else:   
                        logging.info('ROOTKEY %s WAS NOT FOUND' % rootKey)              
            else:
                point.supportingPointsRoots = []
                point.supportingPointsLastChange = []
            point.put()
            logging.info('Updating %s' % point.title)
            i = i + 1 
           
        template_values = {
            'message': "Edits made: %d" % i
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
