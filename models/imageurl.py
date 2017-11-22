import re
import constants
import urllib

class ImageUrl(object):
    """ Descriptor for Point """
    HTTP_RE = re.compile('^https?:\/\/')

    def __init__(self, format):
        self.format = format

    def __get__(self, instance, instance_type):
        if instance.imageURL:
            if self.HTTP_RE.match(instance.imageURL):
                return instance.imageURL
            else:
                return constants.CDN + '/' + self.format + '-' + urllib.quote(instance.imageURL.encode('utf8'))
