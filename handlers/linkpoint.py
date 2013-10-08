import json
import os
import constants
from google.appengine.ext.webapp import template


from authhandler import AuthHandler
from models.point import Point
from models.whysaurusexception import WhysaurusException

class LinkPoint(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        supportingPoint, supportingPointRoot = Point.getCurrentByUrl(self.request.get('supportingPointURL'))
        oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))
        user = self.current_user
        linkType = self.request.get('linkType')

        if user:
            try:
                newLink = [{'pointRoot':supportingPointRoot,
                            'pointCurrentVersion':supportingPoint,
                            'linkType':self.request.get('linkType')}
                            ]
                oldPoint.update(
                    pointsToLink=newLink,
                    user=user
                )
            except WhysaurusException as e:
                resultJSON = json.dumps({'result': False, 'error': str(e)})
            else:
                path = os.path.join(constants.ROOT, 'templates/pointBox.html')
                newLinkPointHTML = json.dumps(template.render(path, {'point': supportingPoint}))
                resultJSON = json.dumps({'result': True,
                                         'numLinkPoints': supportingPoint.linkCount(linkType),
                                         'newLinkPoint':newLinkPointHTML})
        else:
            resultJSON = json.dumps({'result': 'ACCESS DENIED!'})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
