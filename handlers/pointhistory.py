import os
import constants
import json

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point

class PointHistory(AuthHandler):
    def get(self):
        pointData = Point.getFullHistory(self.request.get('pointUrl'))

        template_values = {
            'latestPoint': pointData[0]["point"] if pointData else None,
            'numPoints': len(pointData) if pointData else 0,
            'pointData': pointData,
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')

        }
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        json_values = {
            'historyHTML': self.template_render('pointHistory.html', template_values)
        }
        self.response.out.write(json.dumps(json_values))

    """ should this get replaced by adding fields to the database?  """  
    def getPointCreator(self):
        result = {'result': False}
        point, pointRoot = Point.getCurrentByUrl(self.request.get('pointURL'))
        versionsOfThisPoint = Point.query(ancestor=pointRoot.key).order(Point.version)
        firstVersion = versionsOfThisPoint.get()
        
        authors = []
        """code for listing number of contributors"""
        """
        for point in versionsOfThisPoint:
            thisAuthor = {"authorName": point.authorName, "authorURL": point.authorURL }
            if thisAuthor not in authors:
                authors.append(thisAuthor)
        """                
        
        resultJSON = json.dumps({
                    'result': True, 
                    'creatorName' : firstVersion.authorName,
                    'creatorURL'  : firstVersion.authorURL,
                    'numAuthors'  : len(authors)
                })
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON) 
        
        
        
        
        