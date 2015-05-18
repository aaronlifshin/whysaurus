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
        
    def shouldRedirectToAssignments(self, assignments, currentAssignment):
        if assignments is None:
            return False
            
        if len(assignments) == 0:
            return False
            
        if currentAssignment is not None:
            return False
            
        if 'currentAssignment' not in self.session:
            return True
            
        if self.session['currentAssignment'] == "browseWithoutAssignment":
            return False
            
        return True
        
    @ndb.toplevel    
    def get(self):
        user = None
        currentAssignment = None
        documents = None
        showManifesto = 1
    
        currentArea = self.session.get('currentArea')
        if currentArea and currentArea != '':
            showManifesto = 0
            
            # "browseWithoutAssignment"
            assignmentToSet = self.request.get('setAssignment')
            
            if assignmentToSet:
                self.session['currentAssignment'] = assignmentToSet

            currentAssignment, documents = self.getCurrentAssignment()
            
        if self.logged_in:
            user = self.current_user

        newPoints = yield PointRoot.getRecentCurrentPoints_async(user, currentAssignment)
        featuredPoint = FeaturedPoint.getFeaturedPoint()
        assignments = Assignment.getAll()
        
        # Normal user
        # Case 1: List of points
        # Classroom user
        # Case 1: List of points (but in classroom area, no assignment exists)
        # Case 2: List of assignments (at least one assignment exists and they haven't chosen one or null)
        # Case 3: List of points (assignment on the side, they chose an assignment)
        # Case 4: List of points (chose null assignment)
        
        if self.shouldRedirectToAssignments(assignments, currentAssignment):
            self.redirect('/assignments')
        
        # GET RECENTLY VIEWED
        if user:
            recentlyViewedPoints = user.getRecentlyViewed()
            user.getActiveNotifications()
        else:
            recentlyViewedPoints = []

        layout = 'layout_twoColumns_84.html'
        if currentAssignment:
            layout = 'layout_withAssignment.html'        

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
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
            'layout': layout
        }
        self.response.out.write(self.template_render('index.html', template_values))
