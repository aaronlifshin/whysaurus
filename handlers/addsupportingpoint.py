import json
import os
import constants
import logging
from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point
from models.source import Source
from models.whysaurusexception import WhysaurusException
from models.reportEvent import ReportEvent

class AddSupportingPoint(AuthHandler):
    def post(self):
        jsonOutput = {'result': False}
        user = self.current_user
        linkType = self.request.get('linkType')
        sourcesURLs=json.loads(self.request.get('sourcesURLs'))
        sourcesNames=json.loads(self.request.get('sourcesNames'))
        
        if user:   
            try:       
                parentPointURL = self.request.get('pointUrl')
                oldPoint, oldPointRoot = Point.getCurrentByUrl(parentPointURL)
                if oldPointRoot:
                    newPoint, newLinkPoint = Point.addSupportingPoint(
                        oldPointRoot=oldPointRoot,
                        title=self.request.get('title'),
                        content=self.request.get('content'),
                        summaryText=self.request.get('plainText'),
                        user=user,
                        # backlink=oldPoint.key.parent(),
                        linkType = linkType,
                        imageURL=self.request.get('imageURL'),
                        imageAuthor=self.request.get('imageAuthor'),
                        imageDescription=self.request.get('imageDescription'),
                        sourcesURLs=sourcesURLs,
                        sourcesNames=sourcesNames            
                    )
                else:
                    raise WhysaurusException('Point with URL %s not found' % parentPointURL)
            except WhysaurusException as e:
                jsonOutput = {
                    'result': False,
                    'errMessage': str(e)
                }
            else:
                ReportEvent.queueEventRecord(user.key.urlsafe(), newLinkPoint.key.urlsafe(), newPoint.key.urlsafe(), "Create Point")           
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
            self.response.headers["Content-Type"] = 'application/json; charset=utf-8'      
            self.response.out.write(json.dumps(jsonOutput))
        else:
            self.response.out.write('Need to be logged in')
