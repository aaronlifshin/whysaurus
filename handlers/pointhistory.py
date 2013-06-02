import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class PointHistory(AuthHandler):
    def get(self):
        pointData = Point.getFullHistory(self.request.get('pointUrl'))

        template_values = {
            'latestPoint': pointData[0]["point"] if pointData else None,
            'numPoints': len(pointData) if pointData else 0,
            'pointData': pointData,
            'user': self.current_user
        }

        path = os.path.join(constants.ROOT, 'templates/pointHistory.html')
        self.response.out.write(template.render(path, template_values))
