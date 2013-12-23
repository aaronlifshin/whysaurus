import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class About(AuthHandler):
    def get(self):
        template = self.jinja2_env.get_template('about.html')        
        path = os.path.join(constants.ROOT, 'templates/about.html')
        self.response.out.write(template.render({'user': self.current_user, 
                                                       'currentArea':self.session.get('currentArea')
}))


class Help(AuthHandler):
    def get(self):
        template = self.jinja2_env.get_template('help.html')        
        self.response.out.write(template.render({'user': self.current_user, 
                                                       'currentArea':self.session.get('currentArea')
}))


class Contact(AuthHandler):
    def get(self):
        template = self.jinja2_env.get_template('contact.html')        
        self.response.out.write(template.render({'user': self.current_user,
                                                       'currentArea':self.session.get('currentArea')
}))
