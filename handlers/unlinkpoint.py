import json
from authhandler import AuthHandler
from models.point import Point

class UnlinkPoint(AuthHandler):
    def post(self):

        resultJSON = json.dumps({'result': False})
        if self.current_user:
            if self.request.get('mainPointURL'):
                mainPoint, pointRoot = Point.getCurrentByUrl(self.request.get('mainPointURL'))
                if self.request.get('supportingPointURL'):
                    supportingPointURL = self.request.get('supportingPointURL')
                    newVersion = mainPoint.unlink(self.request.get('supportingPointURL'), 
                                                  self.request.get('linkType'), 
                                                  self.current_user)
                    if newVersion:
                        resultJSON = json.dumps({
                            'result': True, 
                            'pointURL': supportingPointURL,
                            'authorURL': self.current_user.url,
                            'author': newVersion.authorName, 
                            'dateEdited': newVersion.PSTdateEdited.strftime('%b. %d, %Y, %I:%M %p'),
                        })
            else:
               resultJSON = json.dumps({'result': False, 'error': 'URL of main point was not supplied.'})                
        else:
            resultJSON = json.dumps({'result': False, 'error': 'You appear not to be logged in.'})
            
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
