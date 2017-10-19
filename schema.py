from google.appengine.ext import ndb

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.point import Point as PointModel

class Point(NdbObjectType):
    class Meta:
        model = PointModel
        interfaces = (relay.Node,)

    supportingPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_supportingPoints(self, info, **args):
        points = self.getLinkedPoints("supporting", None)
        return points or []

    counterPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_counterPoints(self, info, **args):
        points = self.getLinkedPoints("counter", None)
        return points or []

class SubPointConnection(relay.Connection):
    class Meta:
        node = Point

    class Edge:
        relevance = graphene.Float()
        def resolve_relevance(self, info, **args):
            return self.node._linkInfo.rating

class Query(graphene.ObjectType):
    points = NdbConnectionField(Point)

    def resolve_points(self, info, **args):
        return PointModel.query()

# class Mutation(graphene.ObjectType):
#     introduce_ship = IntroduceShip.Field()


schema = graphene.Schema(query=Query)
#, mutation=Mutation)


# test with:
# curl localhost:8081/graphql -d 'query GetPoints {
#   points {
#     title, upVotes, supportingPoints
#   }
# }'
