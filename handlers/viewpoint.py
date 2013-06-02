import os
import constants
from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.redirecturl import RedirectURL

class ViewPoint(AuthHandler):
    def get(self, pointURL):
        # check if dev environment for Disqus
        devInt = 1 if constants.DEV else 0

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
            pointData = Point.getFullHistory(pointURL)
            supportingPoints = point.getSupportingPoints()
            user = self.current_user
            if not user or not user.userVotes or not point.key.parent() in user.userVotes:
                voteValue = 0
            else:
                voteValue = user.userVotes[point.key.parent()].value

            addedToRecentlyViewed = False
            if user:
                addedToRecentlyViewed = user.updateRecentlyViewed(point.key.parent())

            # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
            if addedToRecentlyViewed or not user:
                pointRoot.addViewCount()

            template_values = {
                'point': point,
                'pointRoot': pointRoot,
                'pointData': pointData,
                'numPoints': len(pointData) if pointData else 0,
                'supportingPoints': supportingPoints,
                'numSupportingPoints': len(supportingPoints) if supportingPoints else 0,
                'user': user,
                'devInt': devInt,  # For Disqus
                'voteValue': voteValue,
                'thresholds': constants.SCORETHRESHOLDS
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/point.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.response.out.write('Could not find point: ' + pointURL)
