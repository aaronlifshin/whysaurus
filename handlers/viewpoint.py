import os
import constants
import logging

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.redirecturl import RedirectURL

class ViewPoint(AuthHandler):
    def createTemplateValues(self, point, pointRoot):
        devInt = 1 if constants.DEV else 0
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

        template_values = {
            'point': point,
            'pointRoot': pointRoot,
            'recentlyViewedPoints': recentlyViewed,
            'supportingPoints': supportingPoints,
            'counterPoints': counterPoints,
            'supportedPoints':pointRoot.getBacklinkPoints("supporting"),
            'counteredPoints':pointRoot.getBacklinkPoints("counter"),
            'sources': sources,
            'user': user,
            'devInt': devInt,  # For Disqus
            'voteValue': voteValue,
            'ribbonValue': ribbonValue,
            'thresholds': constants.SCORETHRESHOLDS
        }
        return template_values
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
        
    def get(self, pointURL):
        # check if dev environment for Disqus
        logging.info('Viewing Point %s' % pointURL)
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if point is None:
            # Try to find a redirector
            newURL = RedirectURL.getByFromURL(pointURL)
            if newURL:
                self.redirect(str(newURL), permanent=True)
            else:
                self.response.out.write('Could not find point: ' + pointURL)
                return

        if point:
            template_values = self.createTemplateValues(point, pointRoot)
            self.outputTemplateValues(template_values)
        else:
            self.response.out.write('Could not find point: ' + pointURL)
