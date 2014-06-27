import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class About(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('about.html', 
                {'user': user, 
                 'currentArea':self.session.get('currentArea')}))


class Help(AuthHandler):
    def get(self):      
        user = self.current_user
        if user:
            user.getActiveNotifications()  
        self.response.out.write(
            self.template_render('help.html', 
                {'user': user, 
                'currentArea':self.session.get('currentArea')}))


class Contact(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('contact.html',
                {'user': user,
                'currentArea':self.session.get('currentArea')}))

class Manifesto(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('manifesto.html',
                {'user': user,
                'currentArea':self.session.get('currentArea')}))
                
class Education(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('education.html',
                {'user': user,
                'currentArea':self.session.get('currentArea')}))
                
class ListSignUp(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('listSignUp.html',
                {'user': user,
                'currentArea':self.session.get('currentArea')}))