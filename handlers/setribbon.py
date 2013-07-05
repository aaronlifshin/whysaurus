import json
from authhandler import AuthHandler
from models.point import Point

class SetRibbon(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        point, pointRoot = Point.getCurrentByUrl(self.request.get('pointURL'))
        user = self.current_user
        if point and user:
            if user.setRibbon(point, bool(self.request.get('ribbon'))):
                resultJSON = json.dumps({'result': True})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
