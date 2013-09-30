import json
import logging
from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.point import Point
from models.source import Source


# AJAX. CALLED FROM THE POINT VIEW PAGE
class EditPoint(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
        sourcesURLs=json.loads(self.request.get('sourcesURLs')) \
            if self.request.get('sourcesURLs') else None
        sourcesNames=json.loads(self.request.get('sourcesNames')) \
            if self.request.get('sourcesNames') else None
        sourcesToRemove=json.loads(self.request.get('sourcesToRemove')) \
            if self.request.get('sourcesToRemove') else None      
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
            sourcesHTML = template.render('templates/sources.html', {'sources':sources})
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
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
