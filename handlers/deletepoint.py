import json
from authhandler import AuthHandler
from models.point import Point

class DeletePoint(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False, 'error': 'Point Not Found'})
        user = self.current_user
        if not user:
            resultJSON = json.dumps({'result': False, 'error': 'Need to be logged in'})
        elif not user.admin:
            resultJSON = json.dumps({'result': False, 'error': 'Must be admin'})
        else:
            urlToDelete = self.request.get('urlToDelete')
            point, pointRoot = Point.getCurrentByUrl(urlToDelete)

            if pointRoot:
                result, error = pointRoot.delete(user)
                if result:
                    resultJSON = json.dumps({'result': True, 'deletedURL': urlToDelete})
                else:
                    resultJSON = json.dumps({'result': False, 'error': error})
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
