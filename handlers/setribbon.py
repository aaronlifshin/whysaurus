import json
from authhandler import AuthHandler
from models.point import Point

class SetRibbon(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        point, pointRoot = Point.getCurrentByUrl(self.request.get('pointURL'))
        user = self.current_user
        newRibbonValue = self.request.get('ribbon') == 'true'
        if point and user:
            if user.setRibbon(point, newRibbonValue):
                resultJSON = json.dumps({'result': True, 'ribbonTotal': point.ribbonTotal})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
