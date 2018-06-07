import os
import constants
import logging
import json
import jinja2

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.redirecturl import RedirectURL


class History(AuthHandler):
    # either url or rootKey needs to be passed in
    @ndb.toplevel
    def createTemplateValues(self, full=True, rootKey=None):
        user = self.current_user
        templateValues = {
            'user': user,
            'currentArea':self.session.get('currentArea'),
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
        }

        if user:
            user.getActiveNotifications()
        templateValues['notifications'] =  user.notifications if user else None,
        raise ndb.Return(templateValues)

    def outputTemplateValues(self, template_values):
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
        html = self.template_render('message.html' if 'message' in template_values else 'react.html', template_values)
        self.response.out.write(html)

    def get(self, pointURL):
        template_values = self.createTemplateValues()
        self.outputTemplateValues(template_values)
