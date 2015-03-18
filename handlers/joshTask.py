import os
import logging
import re

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from models.point import Link
from models.privateArea import PrivateArea
from models.follow import Follow
from models.comment import Comment

from models.whysaurususer import WhysaurusUser

from google.appengine.api import search
from google.appengine.api.taskqueue import Task
from google.appengine.api import namespace_manager
    
from handlers.dbIntegrityCheck import DBIntegrityCheck

from google.appengine.api import namespace_manager



# One-off tasks for changing DB stuff for new versions
class JoshTask(AuthHandler):
    def joshTaskTemp(self):
        results = {'result': False}
        pointRootUrlsafe = self.request.get('rootKey')
        pointRoot = PointRoot.getByUrlsafe(pointRootUrlsafe)
        if pointRoot:
            try: 
                #pointRoot.setTop();
            except WhysaurusException as e:
                results['error'] = str(e)
        else:
            results['error'] = 'Unable to find point root'
            
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)

