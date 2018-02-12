import os
import constants
import datetime
from models.timezones import PST

from google.appengine.ext.webapp import template
from google.appengine.api import mail

from authhandler import AuthHandler

class ContactSend(AuthHandler):
    def post(self):
        mail.send_mail(
            sender='community@whysaurus.com',
            to='community@whysaurus.com',
            subject='WHYSAURUS CONTACT RE: ' + self.request.get('subject') +'  || DATE: '+ str(PST.convert(datetime.datetime.now())),
            body='From: ' + self.request.get('email') + '\n\n' + self.request.get('message'),
            reply_to=self.request.get('email')
        )
        template_values = {
            'message': "Thank you for your message.",
        }      
        self.response.out.write(self.template_render('message.html', template_values))
