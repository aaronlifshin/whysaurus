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
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        json_values = {
            'historyHTML': self.template_render('pointHistory.html', template_values)
        }
        self.response.out.write(json.dumps(json_values))
