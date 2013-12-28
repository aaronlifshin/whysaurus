import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class About(AuthHandler):
    def get(self):
        self.response.out.write(
            self.template_render('about.html', 
                {'user': self.current_user, 
                 'currentArea':self.session.get('currentArea')}))


class Help(AuthHandler):
    def get(self):        
        self.response.out.write(
            self.template_render('help.html', 
                {'user': self.current_user, 
                'currentArea':self.session.get('currentArea')}))


class Contact(AuthHandler):
    def get(self):
        self.response.out.write(
            self.template_render('contact.html',
                {'user': self.current_user,
                'currentArea':self.session.get('currentArea')}))
