import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot

class MainPage(AuthHandler):
    def get(self):

        newPoints = PointRoot.getRecentCurrentPoints()
        user = None

        if self.logged_in:
            user = self.current_user

        # GET RECENTLY VIEWED
        if user:
            recentlyViewedPoints = user.getRecentlyViewed()
        else:
            recentlyViewedPoints = []

        template_values = {
            'recentlyActive': newPoints,
            'recentlyViewed': recentlyViewedPoints,
            'user': user,
            'thresholds': constants.SCORETHRESHOLDS,
            'currentArea':self.session.get('currentArea')
        }
        path = os.path.join(constants.ROOT, 'templates/index.html')
        self.response.out.write(template.render(path, template_values))
