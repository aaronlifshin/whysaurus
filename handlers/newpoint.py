import json
import logging
from authhandler import AuthHandler
from models.point import Point
from models.source import Source
from models.reportEvent import ReportEvent

from google.appengine.ext import ndb

class NewPoint(AuthHandler):
    @ndb.toplevel
    def newPoint(self):        
        user = self.current_user
        sessionAssignmentKey = self.getCurrentAssignmentKey()
        resultJSON = json.dumps({'result': False, 'error': 'Not authorized'})
        secretKey = self.request.get('secret')
        
        if not user:            
            if (secretKey == 'myballotsecret'):
                self.loginBySecretKey(secretKey)
                user = self.current_user
                if user:
                    self.response.headers['Access-Control-Allow-Origin'] = '*'

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
                    sourceNames=sourcesNames,
                    sessionAssignmentKey=sessionAssignmentKey)
                       
                if newPoint:                    
                    recentlyViewed, sources = yield user.getRecentlyViewed_async( \
                                excludeList=[newPoint.key.parent()] + \
                                newPoint.getLinkedPointsRootKeys("supporting") + \
                                newPoint.getLinkedPointsRootKeys("counter")), \
                            newPoint.getSources_async()
                    
                    currentAssignment, documents = self.getCurrentAssignment()
                    
                    templateValues = {
                        'point': newPoint,
                        'pointRoot': newPointRoot,
                        'recentlyViewedPoints': recentlyViewed,
                        'supportingPoints': None,
                        'counterPoints': None,
                        'supportedPoints':newPointRoot.getBacklinkPoints("supporting"),
                        'counteredPoints':newPointRoot.getBacklinkPoints("counter"),
                        'sources': sources,
                        'user': user,
                        'voteValue': 0,
                        'ribbonValue': False,
                        'currentAssignment': currentAssignment,
                        'documents': documents,
                        'currentArea': self.session.get('currentArea'),
                        'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
                    }
                    html = self.template_render('pointContent.html', templateValues)
                    
                    rightColumnHTML = ""
                    if currentAssignment:
                        rightColumnHTML = self.template_render('assignment.html', templateValues)                        
                    else:
                        templateValues = {
                            'user': self.current_user,                
                            'pointRoot': newPointRoot,
                            'comments': None
                        }
                        rightColumnHTML = self.template_render('pointComments.html', templateValues)
                        
                    resultJSON = json.dumps({'result': True, 
                                     'pointURL': newPoint.url,
                                     'title':newPoint.title,
                                     'html': html,
                                     'commentHTML': rightColumnHTML,
                                     'rootKey': newPointRoot.key.urlsafe()
                                 })
                    ReportEvent.queueEventRecord(user.key.urlsafe(), newPoint.key.urlsafe(), None, "Create Point") 
                else:
                    resultJSON = json.dumps({'result': False, 'error': 'Failed to create point.'})
        else:
            resultJSON = json.dumps({'result': False, 'error': 'You appear not to be logged in.'})

        self.response.headers["Pragma"]="no-cache"
        self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"  
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)

