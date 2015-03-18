import os
import constants

from google.appengine.ext.webapp import template
from google.appengine.api import mail

from authhandler import AuthHandler

class ContactSend(AuthHandler):
    def post(self):
        mail.send_mail(
            sender='aaron@whysaurus.com',
            to='aaronlifshin@gmail.com',
            subject='WHYSAURUS CONTACT RE: ' + self.request.get('subject'),
            body='From: ' + self.request.get('name') + '\n' + self.request.get('message'),
            reply_to=self.request.get('email')
        )

        template_values = {
            'message': "Thank you for your message.",
        }      
        self.response.out.write(self.template_render('message.html', template_values))
