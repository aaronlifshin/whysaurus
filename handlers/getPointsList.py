import os
import constants
import json

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot

class GetPointsList(AuthHandler):
    def post(self):      
        points = None
        user = None

        if self.logged_in:
            user = self.current_user
            
        listType = self.request.get('type')
        
        if listType == 'topAwards':
            points = PointRoot.getTopAwardPoints(user)
        elif listType == 'topViewed':
            points = PointRoot.getTopViewedPoints(user)
        elif listType == 'topRated':
            points = PointRoot.getTopRatedPoints(user)
        elif listType == 'editorsPics':
            points = PointRoot.getEditorsPicks(user)

        template_values = {
            'points':points
        }                        
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(json.dumps(
            self.template_render('pointBoxList.html', template_values)))

