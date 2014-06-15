import json
import os
import constants
import logging
from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point
from models.source import Source
from models.whysaurusexception import WhysaurusException

class AddSupportingPoint(AuthHandler):
    def post(self):
        jsonOutput = {'result': False}
        oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('pointUrl'))
        user = self.current_user
        linkType = self.request.get('linkType')
        sourcesURLs=json.loads(self.request.get('sourcesURLs'))
        sourcesNames=json.loads(self.request.get('sourcesNames'))
        if user:
            newLinkPoint, newLinkPointRoot = Point.create(
                title=self.request.get('title'),
                content=self.request.get('content'),
                summaryText=self.request.get('plainText'),
                user=user,
                backlink=oldPoint.key.parent(),
                linktype = linkType,
                imageURL=self.request.get('imageURL'),
                imageAuthor=self.request.get('imageAuthor'),
                imageDescription=self.request.get('imageDescription'),
                sourceURLs=sourcesURLs,
                sourceNames=sourcesNames)
            try:
                newLinks = [{'pointRoot':newLinkPointRoot,
                            'pointCurrentVersion':newLinkPoint,
                            'linkType':linkType},
                            ]
                newPoint = oldPoint.update(
                    pointsToLink=newLinks,                 
                    user=user
                )            
                user.addRelevanceVote(
                  oldPointRoot.key.urlsafe(), 
                  newLinkPointRoot.key.urlsafe(), linkType, 100)                    
            except WhysaurusException as e:
                jsonOutput = {
                    'result': False,
                    'err': str(e)
                }
            else:
                self.response.headers["Content-Type"] = 'application/json; charset=utf-8'                
                newLinkPointHTML = self.template_render('linkPoint.html', {
                    'point': newLinkPoint,
                    'linkType': linkType
                })
                jsonOutput = {
                    'result': True,
                    'version': newPoint.version,
                    'author': newPoint.authorName,
                    'dateEdited': newPoint.PSTdateEdited.strftime('%b. %d, %Y, %I:%M %p'),
                    'numLinkPoints': newPoint.linkCount(linkType),
                    'newLinkPoint': newLinkPointHTML,
                    'authorURL': self.current_user.url
                }
            logging.info(json.dumps(jsonOutput))                
            self.response.out.write(json.dumps(jsonOutput))
        else:
            self.response.out.write('Need to be logged in')
