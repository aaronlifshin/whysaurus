import os
import logging

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

from pprint import pformat

class Profile(AuthHandler):
    def get(self):
        template_values = { 'user': self.current_user, 'user_debug': pformat(self.current_user) }
        path = os.path.join(os.path.dirname(__file__), '../templates/profile.html')
        self.response.out.write(template.render(path, template_values))