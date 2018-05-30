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


class PointCard(AuthHandler):
    # either url or rootKey needs to be passed in
    @ndb.toplevel
    def createTemplateValues(self, url=None, full=True, rootKey=None):
        newURL = None
        templateValues = {}
        point = None
        pointRoot = None

        if url:
            point, pointRoot = yield Point.findCurrent_async(url)
            if point.url != url:
                self.redirect(str(point.url))
        else:
            templateValues = {
               'user': self.current_user,
               'message': "URL or Key must be supplied.",
               'currentArea': self.session.get('currentArea'),
               'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
            }

        if not point:
            templateValues = {
               'user': self.current_user,
               'message': "Could not find point. Some points are in private classrooms and you \
               need to be logged in and authorized to view them.",
               'currentArea': self.session.get('currentArea'),
               'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
            }
        else:   # we have a point!
            user = self.current_user

            if user:
                user.updateRecentlyViewed(point.key.parent())
                user.getActiveNotifications()
            templateValues = {
                'user': user,
                'currentArea':self.session.get('currentArea'),
                'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'notifications': user.notifications if user else None
            }

        self.add_react_json(templateValues)
        raise ndb.Return(templateValues)

    def add_react_json(self, templateValues):
        j = {
            # 'point': templateValues['point'].shortJSON(),
            # 'pointRoot': templateValues['pointRoot']
        }
        templateValues['json'] = json.dumps(j)
        templateValues

    def outputTemplateValues(self, template_values):
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
        html = self.template_render('message.html' if 'message' in template_values else 'pointCard.html', template_values)
        self.response.out.write(html)

    def get(self, pointURL):
        template_values = self.createTemplateValues(pointURL)
        self.outputTemplateValues(template_values)
