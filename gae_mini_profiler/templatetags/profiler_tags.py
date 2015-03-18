# use json in Python 2.7, fallback to simplejson for Python 2.5
try:
    import json
except ImportError:
    import simplejson as json

from gae_mini_profiler import profiler
from google.appengine.ext.webapp import template

from django.template import Library
register = Library()
import logging

def profiler_includes_request_id(request_id, show_immediately=False):
    if not request_id:
        return ""

    js_path = "/gae_mini_profiler/static/js/profiler.js"
    css_path = "/gae_mini_profiler/static/css/profiler.css"

    return """
<link rel="stylesheet" type="text/css" href="%s" />
<script type="text/javascript" src="%s"></script>
<script  type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/angularjs/1.2.6/angular.min.js"></script>
<script type="text/javascript">GaeMiniProfiler.init("%s", %s)</script>
    """ % (css_path, js_path, request_id, json.dumps(show_immediately))

def profiler_includes_str():
    return profiler_includes_request_id(profiler.CurrentRequestId.get())
    
register = template.create_template_register()
@register.simple_tag
def profiler_includes():
    return profiler_includes_str()
