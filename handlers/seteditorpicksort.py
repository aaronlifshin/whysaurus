import os

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import PointRoot

class SetEditorPickSort(AuthHandler):
    def get(self):
        countSaved = 0
        pointsRootsQuery = PointRoot.gql("WHERE editorsPick = TRUE")
        pointRoots = pointsRootsQuery.fetch(100)
        for pointRoot in pointRoots:
            pointRoot.editorsPickSort = 100000
            pointRoot.put()
            countSaved = countSaved + 1
        template_values = {
            'message': "Edits made: %d" % countSaved
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        