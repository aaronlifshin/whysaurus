import os
import constants
import json

from google.appengine.ext import ndb

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot

class GetPointsList(AuthHandler):
    @ndb.toplevel        
    def post(self):      
        points = None
        user = None

        if self.logged_in:
            user = self.current_user
            
        listType = self.request.get('type')
        
        # NO LONGER USING "most ribbons"
        # if listType == 'topAwards':
        #    points = PointRoot.getTopAwardPoints(user)
        if listType == 'topViewed':            
            points = yield PointRoot.getTopViewedPoints_async(user)
        elif listType == 'topRated':
            points = yield PointRoot.getTopRatedPoints_async(user)
        elif listType == 'editorsPics':
            points = yield PointRoot.getEditorsPicks_async(user)

        template_values = {
            'points':points
        }                        
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(json.dumps(
            self.template_render('pointBoxList.html', template_values)))

