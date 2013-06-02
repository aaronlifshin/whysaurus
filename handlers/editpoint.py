import json
from authhandler import AuthHandler
from models.point import Point

# AJAX. CALLED FROM THE POINT VIEW PAGE
class EditPoint(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
        newVersion = oldPoint.update(
            newTitle=self.request.get('title'),
            newContent=self.request.get('content'),
            newSummaryText=self.request.get('plainText'),
            user=self.current_user,
            imageURL=self.request.get('imageURL'),
            imageAuthor=self.request.get('imageAuthor'),
            imageDescription=self.request.get('imageDescription')
        )
        if newVersion:
            resultJSON = json.dumps({
                'result': True,
                'version': newVersion.version,
                'author': newVersion.authorName,
                'dateEdited': str(newVersion.dateEdited),
                'pointURL':newVersion.url,
                'imageURL': newVersion.imageURL,
                'imageAuthor': newVersion.imageAuthor,
                'imageDescription': newVersion.imageDescription
            })
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
