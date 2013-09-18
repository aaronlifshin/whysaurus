import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class About(AuthHandler):
    def get(self):
        path = os.path.join(constants.ROOT, 'templates/about.html')
        self.response.out.write(template.render(path, {'user': self.current_user, 
                                                       'currentArea':self.session.get('currentArea')
}))


class Help(AuthHandler):
    def get(self):
        path = os.path.join(constants.ROOT, 'templates/help.html')
        self.response.out.write(template.render(path, {'user': self.current_user, 
                                                       'currentArea':self.session.get('currentArea')
}))


class Contact(AuthHandler):
    def get(self):
        path = os.path.join(constants.ROOT, 'templates/contact.html')
        self.response.out.write(template.render(path, {'user': self.current_user,
                                                       'currentArea':self.session.get('currentArea')
}))
