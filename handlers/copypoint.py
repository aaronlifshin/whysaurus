import json
import os
import constants
import logging
from google.appengine.ext.webapp import template


from authhandler import AuthHandler
from models.point import Point
from models.uservote import RelevanceVote
from models.whysaurusexception import WhysaurusException

class CopyPoint(AuthHandler):
    def post(self):
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'        
        result = {'result': False}
        point, pointRoot = Point.getCurrentByUrl(self.request.get('pointUrl'))
        areaName = self.request.get('areaName')
                
        user = self.current_user
        sessionAssignmentKey = self.getCurrentAssignmentKey()       

        if user and user.isAdmin:
            if point:
                pointRoot.copy(point, areaName)
                result['result'] = True
            else:
                result['error'] =  'Not able to fund point'
        else:
            result['error'] =  'User must be logged in and must be admin. ACCESS DENIED!'
        self.response.out.write(json.dumps(result))
