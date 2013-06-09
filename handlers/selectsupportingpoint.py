import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class SelectSupportingPoint(AuthHandler):
    def post(self):
        user = self.current_user
        # GET RECENTLY VIEWED
        if user:
            oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))
            recentlyViewedPoints = user.getRecentlyViewed(
                excludeList=[oldPoint.key.parent()] + oldPoint.supportingPointsRoots
            )
        else:
            recentlyViewedPoints = []

        templateValues = {
            'points': recentlyViewedPoints,
            'parentPoint': oldPoint,
            'user': user,
            'thresholds': constants.SCORETHRESHOLDS
        }
        path = os.path.join(constants.ROOT, 'templates/selectSupportingPoint.html')
        self.response.out.write(template.render(path, templateValues))
