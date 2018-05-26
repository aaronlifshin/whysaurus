import os
import constants
import json
import logging 
from google.appengine.ext import ndb

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class SearchFromHeader(AuthHandler):
    @ndb.toplevel
    def get(self):
        searchString = self.request.get('q')
        searchResultsFuture = Point.search(
            user=self.current_user, 
            searchTerms=searchString
        )
        searchResults = None
        if searchResultsFuture:
            searchResults = searchResultsFuture.get_result()
                        
        result = len(searchResults) if searchResults else 0
        template_values = {
            'searchResults': searchResults,
            'searchString': searchString,
        }
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'        
        html = self.template_render('searchResults.html', template_values)
        json_values = {'html':html,
                       'searchString': searchString,
                       'result':result
                       }
        self.response.out.write(json.dumps(json_values))