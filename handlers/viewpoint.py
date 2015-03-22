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


class ViewPoint(AuthHandler):
    # either url or rootKey needs to be passed in
    @ndb.toplevel
    def createTemplateValues(self, url=None, full=True, rootKey=None):
        newURL = None
        templateValues = {}
        point = None
        pointRoot = None
        
        if url:
            point, pointRoot = yield Point.findCurrent_async(url)
        elif rootKey:
            point, pointRoot = Point.getCurrentByRootKey(rootKey)  
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
            voteValue = 0
            ribbonValue = False
            addedToRecentlyViewed = False                        
            user = self.current_user    
            
            # supportingPoints, counterPoints = point.getAllLinkedPoints(user)
          
            # We need to get the recently viewed points here
            # Because the user can add them as counter/supporting points
            if user:                
                vote, relevanceVotes, recentlyViewed, sources, supportingPoints, counterPoints = yield \
                    user.getVote_async(point.key.parent()), \
                    user.getRelevanceVotes_async(point), \
                    user.getRecentlyViewed_async( \
                        excludeList=[point.key.parent()] + \
                        point.getLinkedPointsRootKeys("supporting") + \
                        point.getLinkedPointsRootKeys("counter")), \
                    point.getSources_async(), \
                    point.getLinkedPoints_async("supporting", user), \
                    point.getLinkedPoints_async("counter", user)
                point.addRelevanceVotes(relevanceVotes, supportingPoints, counterPoints)

                addedToRecentlyViewed = user.updateRecentlyViewed(point.key.parent())
            else:
                sources, supportingPoints, counterPoints = yield point.getSources_async(), \
                    point.getLinkedPoints_async("supporting", None), \
                    point.getLinkedPoints_async("counter", None)
                recentlyViewed = None
            
            # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
            if addedToRecentlyViewed or not user:
                viewCountFuture = pointRoot.addViewCount()
        
            if user:
                voteValue = vote.value if vote else 0
                ribbonValue = vote.ribbon if vote else False
                
            currentAssignment, documents = self.getCurrentAssignment()
            # viewCountFuture.get_result()
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
                'currentAssignment': currentAssignment,
                'documents': documents,
                'currentArea':self.session.get('currentArea'),
                'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
            }
            
            if full:
                if user:
                    user.getActiveNotifications()
                templateValues['notifications'] =  user.notifications if user else None,
                templateValues['comments'] = pointRoot.getComments()
                                
        raise ndb.Return(templateValues)          
    
    def outputTemplateValues(self, template_values):
        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"  
        html = self.template_render('message.html' if 'message' in template_values else 'point.html', template_values)
        self.response.out.write(html)
        
    def post(self, pointURL):
        rootKey = self.request.get('rootKey')
        template_values = self.createTemplateValues(rootKey=rootKey)        
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
            template_values = {
                'user': self.current_user,                
                'pointRoot': pointRoot,
                'comments':pointRoot.getComments()
            }        
            html = self.template_render('pointComments.html', template_values)
            resultJSON = json.dumps({
                'result': True,
                'html': html
            }) 
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON) 
                  
    def getPointContent(self):  
        resultJSON = json.dumps({'result': False})

        url = self.request.get('url')        
        vals = self.createTemplateValues(url, full=False)
        
        if 'point' in vals: 
            html = self.template_render('pointContent.html', vals)

            resultJSON = json.dumps({
                'result': True,
                'title' : vals['point'].title,
                'url': vals['point'].url,
                'myVote': vals['voteValue'],
                'html': html,
            })  
            
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
                                
    def get(self, pointURL):        
        template_values = self.createTemplateValues(pointURL) 
        self.outputTemplateValues(template_values)
           
