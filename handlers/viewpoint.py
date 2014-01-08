import os
import constants
import logging
import json
import jinja2

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.redirecturl import RedirectURL


class ViewPoint(AuthHandler):
    def createTemplateValues(self, point, pointRoot, full=True):
        user = self.current_user    
        supportingPoints, counterPoints = point.getAllLinkedPoints(user)
        sources = point.getSources()

        voteValue = 0
        ribbonValue = False
        if user:
            voteFuture = user.getVoteFuture(point.key.parent())
            # voteValue, ribbonValue = user.getVoteValues(point.key.parent())
        
        # We need to get the recently viewed points here
        # Because the user can add them as counter/supporting points
        addedToRecentlyViewed = False
        if user:
            recentlyViewed = user.getRecentlyViewed(
                excludeList=[point.key.parent()] + \
                point.getLinkedPointsRootKeys("supporting") + \
                point.getLinkedPointsRootKeys("counter")
            )

            addedToRecentlyViewed = user.updateRecentlyViewed(point.key.parent())
        else:
            recentlyViewed = None
            
        # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
        if addedToRecentlyViewed or not user:
            pointRoot.addViewCount()
        
        if user:
            vote = voteFuture.get_result()
            voteValue = vote.value if vote else 0
            ribbonValue = vote.ribbon if vote else False


        templateValues = {
            'point': point,
            'pointRoot': pointRoot,
            'recentlyViewedPoints': recentlyViewed,
            'supportingPoints': supportingPoints,
            'counterPoints': counterPoints,
            'supportedPoints':pointRoot.getBacklinkPoints("supporting"),
            'counteredPoints':pointRoot.getBacklinkPoints("counter"),
            'sources': sources,
            'user': user,
            'voteValue': voteValue,
            'ribbonValue': ribbonValue,
            'thresholds': constants.SCORETHRESHOLDS,
            'currentArea':self.session.get('currentArea'),
        }
        
        if full:
            if user:
                user.getActiveNotifications()
            additionalValues = {
                'notifications': user.notifications if user else None,
                'comments': pointRoot.getComments()
            }
            templateValues = dict(templateValues.items() + additionalValues.items())
            
        return templateValues
    
    def outputTemplateValues(self, template_values):
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
        html = self.template_render('point.html', template_values)
        self.response.out.write(html)
        
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
                'comments':pointRoot.getComments(),
            }        
            html = self.template_render('pointComments.html', tv)
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
            html = self.template_render('pointContent.html', vals)

            resultJSON = json.dumps({
                'result': True,
                'title' : point.title,
                'url': point.url,
                'myVote': vals['voteValue'],
                'html': html,
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
            self.response.out.write(self.template_render('message.html', template_values ))      
