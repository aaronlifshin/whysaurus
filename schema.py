from google.appengine.ext import ndb

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.point import Point as PointModel

class Point(NdbObjectType):
    class Meta:
        model = PointModel
#        interfaces = (relay.Node,)

class Query(graphene.ObjectType):
    points = graphene.List(Point)

    @graphene.resolve_only_args
    def resolve_points(self):
        return PointModel.query()

# class Mutation(graphene.ObjectType):
#     introduce_ship = IntroduceShip.Field()


schema = graphene.Schema(query=Query)
#, mutation=Mutation)

