import json

from authhandler import AuthHandler
from models.point import Point

class AjaxSearch(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        searchResults = Point.search(self.request.get('searchTerms'), self.request.get('exclude'))
        if searchResults:
            resultJSON = json.dumps({
                'result': True,
                'searchResults': searchResults,
                'searchString': self.request.get('searchTerms')
            })
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
