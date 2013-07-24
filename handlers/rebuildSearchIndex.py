import os
import logging


from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from google.appengine.api import search



class RebuildSearchIndex(AuthHandler):
    def get(self):

        query = PointRoot.query()
        bigMessage = []
        i = 0
        doc_index = search.Index(name="points")

        for pointRoot in query.iter():                     
            doc_index.delete(pointRoot.url)
            doc_index.delete(pointRoot.key.urlsafe())
            pointRoot.getCurrent().addToSearchIndexNew()
            bigMessage.append('Added %s' % pointRoot.url)
            i = i + 1

        bigMessage.append("Insertions made: %d" % i)

        template_values = {
            'message': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))