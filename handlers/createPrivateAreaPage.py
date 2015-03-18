import os
import constants
import logging
import json
import string

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.privateArea import PrivateArea
from models.whysaurusexception import WhysaurusException

class CreatePrivateAreaPage(AuthHandler):
    def get(self):
        self.response.out.write(
            self.template_render('createPrivateAreaPage.html', {}))


