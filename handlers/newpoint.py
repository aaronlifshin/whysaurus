import json
import logging
from authhandler import AuthHandler
from models.point import Point
from models.source import Source


class NewPoint(AuthHandler):
    def post(self):
        user = self.current_user
        resultJSON = json.dumps({'result': False, 'error': 'Not authorized'})
        if user:
            if not self.request.get('title'):                
                resultJSON = json.dumps({'result': False, 'error': 'Your point must have a title'})
            else:
                sourcesURLs=json.loads(self.request.get('sourcesURLs')) if self.request.get('sourcesURLs') else None
                sourcesNames=json.loads(self.request.get('sourcesNames')) if self.request.get('sourcesNames') else None
                newPoint, newPointRoot = Point.create(
                    title=self.request.get('title'),
                    content=self.request.get('content'),
                    summaryText=self.request.get('plainText'),
                    user=user,
                    imageURL=self.request.get('imageURL'),
                    imageAuthor=self.request.get('imageAuthor'),
                    imageDescription=self.request.get('imageDescription'),
                    sourceURLs=sourcesURLs,
                    sourceNames=sourcesNames)
                if newPoint:
                    resultJSON = json.dumps({'result': True, 
                                     'pointURL': newPoint.url,
                                     'rootKey': newPointRoot.key.urlsafe()})
                else:
                    resultJSON = json.dumps({'result': False, 'error': 'Failed to create point.'})
        else:
            resultJSON = json.dumps({'result': False, 'error': 'You appear not to be logged in.'})

        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
