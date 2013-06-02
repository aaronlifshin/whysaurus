import os
import django
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class TestPage(AuthHandler):
    def get(self):
        user = self.current_user
        template_values = {
            'user': user,
            'dv': django.VERSION
        }
        path = os.path.join(constants.ROOT, 'templates/test.html')
        self.response.out.write(template.render(path, template_values))
