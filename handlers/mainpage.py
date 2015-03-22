import os
import constants
import logging
import json

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot, FeaturedPoint
from models.assignment import Assignment
from models.document import Document
from google.appengine.ext import ndb

from webapp2_extras import sessions

class MainPage(AuthHandler):
    
    # NOT USED FOR NOW (doesn't get votes
    def getMainPageLeft(self):
        
        newPoints = PointRoot.getRecentCurrentPoints()
        featuredPoint = FeaturedPoint.getFeaturedPoint()
            
        vals = {
            'recentlyActive': newPoints,
            'featuredPoint': featuredPoint,
            'user': self.current_user
        }
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'        
        html = self.template_render('mainPageLeftColumn.html', vals)
        resultJSON = json.dumps({
            'result': True,
            'html': html,
        }) 
        self.response.out.write(resultJSON) 
        
    def getMainPageRight(self):      
        user = self.current_user
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'        

        if user:
            recentlyViewedPoints = user.getRecentlyViewed()
        else:
            recentlyViewedPoints = []
            
        vals = {
            'recentlyViewed': recentlyViewedPoints,
            'user': user
        }
        html = self.template_render('mainPageRightColumn.html', vals)
        

        resultJSON = json.dumps({
            'result': True,
            'html': html,
        }) 
        self.response.out.write(resultJSON) 
        
    @ndb.toplevel    
    def get(self):
        user = None
        currentAssignment = None
        documents = None
        showManifesto = 1
    
        currentArea = self.session.get('currentArea')
        if currentArea and currentArea != '':
            showManifesto = 0
            
            assignmentToSet = self.request.get('setAssignment')
            if assignmentToSet:
                self.session['currentAssignment'] = assignmentToSet

            currentAssignment, documents = self.getCurrentAssignment()
            
        if self.logged_in:
            user = self.current_user

        newPoints = yield PointRoot.getRecentCurrentPoints_async(user, currentAssignment)
        featuredPoint = FeaturedPoint.getFeaturedPoint()
        assignments = Assignment.getAll()
        
        # GET RECENTLY VIEWED
        if user:
            recentlyViewedPoints = user.getRecentlyViewed()
            user.getActiveNotifications()
        else:
            recentlyViewedPoints = []



        template_values = {
            'recentlyActive': newPoints,
            'recentlyViewed': recentlyViewedPoints,
            'featuredPoint': featuredPoint,
            'user': user,
            'assignments': assignments,
            'showManifesto': showManifesto,
            'thresholds': constants.SCORETHRESHOLDS,
            'currentArea': currentArea,
            'currentAssignment': currentAssignment,
            'documents': documents,
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
        }
        self.response.out.write(self.template_render('index.html', template_values))
