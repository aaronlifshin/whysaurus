import json
from authhandler import AuthHandler
from models.point import Point

class UnlinkPoint(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        if self.request.get('mainPointURL'):
            mainPoint, pointRoot = Point.getCurrentByUrl(self.request.get('mainPointURL'))
            if self.request.get('supportingPointURL'):
                supportingPointURL = self.request.get('supportingPointURL')
                newVersion = mainPoint.unlink(self.request.get('supportingPointURL'), 
                                              self.request.get('linkType'), 
                                              self.current_user)
                if newVersion:
                    resultJSON = json.dumps({'result': True, 'pointURL': supportingPointURL})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
