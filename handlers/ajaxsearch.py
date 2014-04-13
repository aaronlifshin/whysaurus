import os
import json

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
import constants


class AjaxSearch(AuthHandler):
    @ndb.toplevel
    def post(self):
        resultJSON = json.dumps({'result': False})
        searchResultsFuture = Point.search(
            searchTerms=self.request.get('searchTerms'), 
            user=self.current_user,
            excludeURL=self.request.get('exclude'), 
            linkType=self.request.get('linkType') 
        )
        searchResults = None
        if searchResultsFuture:
            searchResults = searchResultsFuture.get_result()
            
        template_values = {
            'points': searchResults,
            'linkType': self.request.get('linkType'),
        }
        resultsHTML = self.template_render('pointBoxList.html', template_values)
        
        if searchResults:
            resultJSON = json.dumps({
                'result': True,
                'resultsHTML': resultsHTML,
                'searchString': self.request.get('searchTerms')
            })
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
