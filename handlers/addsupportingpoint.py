import json

from authhandler import AuthHandler
from models.point import Point
from models.whysaurusexception import WhysaurusException

class AddSupportingPoint(AuthHandler):
    def post(self):
        jsonOutput = {'result': False}
        oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('pointUrl'))
        user = self.current_user
        linkType = self.request.get('linkType')
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
                imageDescription=self.request.get('imageDescription'))
            try:
                newLinks = [{'pointRoot':newLinkPointRoot,
                            'pointCurrentVersion':newLinkPoint,
                            'linkType':linkType},
                            ]
                newPoint = oldPoint.update(
                    pointsToLink=newLinks,                 
                    user=user
                )
            except WhysaurusException as e:
                jsonOutput = {
                    'result': False,
                    'err': str(e)
                }
            else:
                jsonOutput = {
                    'result': True,
                    'version': newPoint.version,
                    'author': newPoint.authorName,
                    'dateEdited': newPoint.dateEdited.strftime("%Y-%m-%d %H: %M: %S %p"),
                    'numLinkPoints': newPoint.linkCount(linkType),
                    'newLinkPoint':newLinkPoint.shortJSON()
                }
            resultJSON = json.dumps(jsonOutput)
            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
            self.response.out.write(resultJSON)
        else:
            self.response.out.write('Need to be logged in')
