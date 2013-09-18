import os
import constants
import json

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot

class GetPointsList(AuthHandler):
    def post(self):      
        points = None
        listType = self.request.get('type')
        if listType == 'topAwards':
            points = PointRoot.getTopAwardPoints()
        elif listType == 'topViewed':
            points = PointRoot.getTopViewedPoints()
        elif listType == 'topRated':
            points = PointRoot.getTopRatedPoints()
        elif listType == 'editorsPics':
            points = PointRoot.getEditorsPicks()

        template_values = {
            'points':points
        }
        path = os.path.join(constants.ROOT, 'templates/pointBoxList.html')
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json.dumps(template.render(path, template_values)))

