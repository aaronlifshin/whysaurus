import json
import logging
from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point, FeaturedPoint
from models.source import Source
from models.reportEvent import ReportEvent

# AJAX. CALLED FROM THE POINT VIEW PAGE
class EditPoint(AuthHandler):
    def post(self):
        user = self.current_user
        if user:        
            resultJSON = json.dumps({'result': False})
            oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
            sourcesURLs=json.loads(self.request.get('sourcesURLs')) \
                if self.request.get('sourcesURLs') else None
            sourcesNames=json.loads(self.request.get('sourcesNames')) \
                if self.request.get('sourcesNames') else None
            sourcesToRemove=json.loads(self.request.get('sourcesToRemove')) \
                if self.request.get('sourcesToRemove') else None    
            if oldPoint == None:
                resultJSON = json.dumps({'result': False, 
                    'error': 'Unable to edit point. Please refresh the page and try again.'})
            else:
                sources = Source.constructFromArrays(sourcesURLs, sourcesNames, oldPoint.key)
                newVersion = oldPoint.update(
                    newTitle=self.request.get('title'),
                    newContent=self.request.get('content'),
                    newSummaryText=self.request.get('plainText'),
                    user=self.current_user,
                    imageURL=self.request.get('imageURL'),
                    imageAuthor=self.request.get('imageAuthor'),
                    imageDescription=self.request.get('imageDescription'),
                    sourcesToAdd=sources,
                    sourceKeysToRemove= sourcesToRemove            
                )
                if newVersion:
                    sources = newVersion.getSources()   
                    sourcesHTML = self.template_render('sources.html', {'sources':sources})
            
                    resultJSON = json.dumps({
                        'result': True,
                        'version': newVersion.version,
                        'author': newVersion.authorName,
                        'authorURL': self.current_user.url,
                        'dateEdited': newVersion.PSTdateEdited.strftime('%b. %d, %Y, %I:%M %p'),
                        'pointURL':newVersion.url,
                        'imageURL': newVersion.imageURL,
                        'imageAuthor': newVersion.imageAuthor,
                        'imageDescription': newVersion.imageDescription,
                        'sourcesHTML': sourcesHTML
                    })
                    ReportEvent.queueEventRecord(user.key.urlsafe(), newVersion.key.urlsafe(), None, "Edit Point")
                else:
                    # This is the only way newVersion will fail
                    resultJSON = json.dumps({'result': False, 'error': 'You appear not to be logged in.'})
                
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)        
        
    def changeEditorsPick(self):
        result = {'result': False}
        try:
            if self.current_user and self.current_user.isAdmin:
                point, pointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
                if not pointRoot:
                    result['error'] = 'Not able to find point by URL'
                pick = True if self.request.get('editorsPick') == 'true' else False
                if pointRoot.updateEditorsPick(pick, 
                                               int(self.request.get('editorsPickSort'))):
                    result = {'result': True}
            else:
                result = {'result': False, 'error': 'Permission denied!'}
        except Exception as e:
            result = {'result': False, 'error': str(e)}
        
        resultJSON = json.dumps(result)    
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
     
    def makeFeatured(self):
        result = {'result': False}
        try:
            if self.current_user and self.current_user.isAdmin:    
                point, pointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
                if not pointRoot:
                    result['error'] = 'Not able to find point by URL'
                if FeaturedPoint.setFeatured(pointRoot.key):
                    result = {'result': True}
            else:
                result = {'result': False, 'error': 'Permission denied!'}
        except Exception as e:
            result = {'result': False, 'error': str(e)}  
             
        resultJSON = json.dumps(result)    
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
     
    def refreshTopStatus(self):
        result = {'result': False}
        try:
            if self.current_user and self.current_user.isAdmin:    
                point, pointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
                if not pointRoot:
                    result['error'] = 'Not able to find point by URL'
                pointRoot.setTop()
                result = {'result': True}
            else:
                result = {'result': False, 'error': 'Permission denied!'}
        except Exception as e:
            result = {'result': False, 'error': str(e)}  
             
        resultJSON = json.dumps(result)    
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)