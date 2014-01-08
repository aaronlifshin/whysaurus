import os
import logging
import json

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from google.appengine.api import search



class Outliner(AuthHandler):
    def get(self):
        template_values = {
            'user':self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        self.response.out.write(
            self.template_render(
                'outliner.html', 
                template_values))
          
       