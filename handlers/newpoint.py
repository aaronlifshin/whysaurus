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
            sourcesURLs=json.loads(self.request.get('sourcesURLs'))
            sourcesNames=json.loads(self.request.get('sourcesNames'))
            rawSources = Source.constructFromArrays(sourcesURLs, sourcesNames)
            newPoint, newPointRoot = Point.create(
                title=self.request.get('title'),
                content=self.request.get('content'),
                summaryText=self.request.get('plainText'),
                user=user,
                imageURL=self.request.get('imageURL'),
                imageAuthor=self.request.get('imageAuthor'),
                imageDescription=self.request.get('imageDescription'),
                sources=rawSources)
        if newPoint:
            resultJSON = json.dumps({'result': True, 
                                     'pointURL': newPoint.url,
                                     'rootKey': newPointRoot.key.urlsafe()})
        else:
            resultJSON = json.dumps({'result': False, 'error': 'Failed to create point.'})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
