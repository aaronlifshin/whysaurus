import logging
import traceback

from authhandler import AuthHandler
from graphene_gae.webapp2 import GraphQLHandler

class WhysaurusGraphQL(GraphQLHandler, AuthHandler):
    def _get_context(self):
        return self

    
