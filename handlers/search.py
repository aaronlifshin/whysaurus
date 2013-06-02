import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class Search(AuthHandler):
    def get(self):
        searchResults = Point.search(self.request.get('searchTerms'))
        template_values = {
            'user': self.current_user,
            'searchResults': searchResults,
            'searchString': self.request.get('searchTerms'),
            'thresholds': constants.SCORETHRESHOLDS
        }
        path = os.path.join(constants.ROOT, 'templates/searchResults.html')
        self.response.out.write(template.render(path, template_values))
