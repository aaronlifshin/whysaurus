import os
import constants
import json

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
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')

        }
        path = os.path.join(constants.ROOT, 'templates/pointHistory.html')
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json.dumps(template.render(path, template_values)))
