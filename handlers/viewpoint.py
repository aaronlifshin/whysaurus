import os
import constants
import logging
import json

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.redirecturl import RedirectURL

class ViewPoint(AuthHandler):
    def createTemplateValues(self, point, pointRoot, full=True):
        supportingPoints = point.getSupportingPoints()
        counterPoints = point.getCounterPoints()
        sources = point.getSources()

        user = self.current_user
        if not user or not user.userVotes or not point.key.parent() in user.userVotes:
            voteValue = 0
            ribbonValue = False
        else:
            voteValue = user.userVotes[point.key.parent()].value
            ribbonValue = user.userVotes[point.key.parent()].ribbon
        addedToRecentlyViewed = False
        recentlyViewed = None
        if user:
            recentlyViewed = user.getRecentlyViewed(excludeList=[point.key.parent()] + \
                                                    point.supportingPointsRoots + \
                                                    point.counterPointsRoots)
            addedToRecentlyViewed = user.updateRecentlyViewed(point.key.parent())

        # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
        if addedToRecentlyViewed or not user:
            pointRoot.addViewCount()

        templateValues = {
            'point': point,
            'pointRoot': pointRoot,
             # 'recentlyViewedPoints': recentlyViewed,
            'supportingPoints': supportingPoints,
            'counterPoints': counterPoints,
            'supportedPoints':pointRoot.getBacklinkPoints("supporting"),
            'counteredPoints':pointRoot.getBacklinkPoints("counter"),
            'sources': sources,
            'user': user,
            'voteValue': voteValue,
            'ribbonValue': ribbonValue,
            'thresholds': constants.SCORETHRESHOLDS,
            'currentArea':self.session.get('currentArea')
        }
        
        if full:
            additionalValues = {
                'notifications': user.notifications if user else None,
                'comments': pointRoot.getComments()
            }
            templateValues = dict(templateValues.items() + additionalValues.items())
            
        return templateValues
    
    def outputTemplateValues(self, template_values):
        path = os.path.join(constants.ROOT, 'templates/point.html')
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
        self.response.out.write(template.render(path, template_values)) 
        
    def post(self, pointURL):
        rootKey = self.request.get('rootKey')
        point, pointRoot = Point.getCurrentByRootKey(rootKey)
        template_values = self.createTemplateValues(point, pointRoot)        
        self.outputTemplateValues(template_values)
     
            
    def getPointComments(self):       
        resultJSON = json.dumps({'result': False})

        newURL = None
        url = self.request.get('url')
        point, pointRoot = Point.getCurrentByUrl(url)
        if point is None:
            # Try to find a redirector
            newURL = RedirectURL.getByFromURL(url)
            if newURL:
                point, pointRoot = Point.getCurrentByUrl(url)   
        if pointRoot:
            tv = {
                'pointRoot': pointRoot,
                'comments':pointRoot.getComments()
            }
            html = template.render('templates/pointComments.html', tv)
            resultJSON = json.dumps({
                'result': True,
                'html': html
            }) 
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON) 
                  
    def getPointContent(self):  
        resultJSON = json.dumps({'result': False})

        newURL = None
        url = self.request.get('url')
        point, pointRoot = Point.getCurrentByUrl(url)
        if point is None:
            # Try to find a redirector
            newURL = RedirectURL.getByFromURL(url)
            if newURL:
                point, pointRoot = Point.getCurrentByUrl(url)
        if point:
            vals = self.createTemplateValues(point, pointRoot, full=False)
            html = template.render('templates/pointContent.html', vals)
            resultJSON = json.dumps({
                'result': True,
                'title' : point.title,
                'url': point.url,
                'myVote': vals['voteValue'],
                'html': html
            })  
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
                                
    def get(self, pointURL):
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if point is None:
            # Try to find a redirector
            newURL = RedirectURL.getByFromURL(pointURL)
            if newURL:
                self.redirect(str(newURL), permanent=True)

        if point:
            template_values = self.createTemplateValues(point, pointRoot)
            self.outputTemplateValues(template_values)
        else:
            template_values = {
                               'user': self.current_user,
                               'message': "Could not find point. \
                               Some points are in private areas and you \
                               need to be logged into those areas to view them.",
                               'currentArea':self.session.get('currentArea')
            }
            path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
            self.response.out.write(template.render(path, template_values ))      
