import os
import constants
import json
import logging
from google.appengine.ext import ndb

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class HeaderSearch(AuthHandler):
    @ndb.toplevel
    def get(self):
        template_values = {
            'searchString': self.request.get('q'),

        }
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
        html = self.template_render('headerSearch.html', template_values)
        self.response.out.write(html)
