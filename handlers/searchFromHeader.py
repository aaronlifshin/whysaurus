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
        # print 'searchString = {0}'.format(searchString)
        searchResultsFuture = Point.search(
            user=self.current_user, 
            searchTerms=searchString
        )
        searchResults = None
        if searchResultsFuture:
            searchResults = searchResultsFuture.get_result()
                        
        print 'searchResults = {0}'.format(searchResults)
        self.response.headers["Content-Type"] = 'text/html; charset=utf-8'
        # self.response.out.write("<div>SearchFromHeader.py</div>")
        # raise ndb.Return(searchResults)
