from google.appengine.ext import ndb

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.point import Point as PointModel

class Point(NdbObjectType):
    class Meta:
        model = PointModel
        interfaces = (relay.Node,)

    numSupporting = graphene.Int()
    def resolve_numSupporting(self, info):
        return self.numSupporting

    numCounter = graphene.Int()
    def resolve_numCounter(self, info):
        return self.numCounter

    numComments = graphene.Int()
    def resolve_numComments(self, info):
        # TODO: need to get a link to the point root and then get numComments from that
        return 42

    supportedCount = graphene.Int()
    def resolve_supportedCount(self, info):
        # TODO: need to get a link to the point root and then get supportedCount from that
        return 42

    supportingPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_supportingPoints(self, info, **args):
        points = self.getLinkedPoints("supporting", None)
        if points:
            for point in points:
                point.link_type = 'supporting'
        return points or []

    counterPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_counterPoints(self, info, **args):
        points = self.getLinkedPoints("counter", None)
        if points:
            for point in points:
                point.link_type = 'counter'
        return points or []

class SubPointConnection(relay.Connection):
    class Meta:
        node = Point

    class Edge:
        relevance = graphene.Float()
        def resolve_relevance(self, info, **args):
            return self.node._linkInfo.rating

        type = graphene.String()
        def resolve_type(self, info, **args):
            # this assumes link_type has been set in the Point.resolve_xxxPoints methods, above
            return self.node.link_type

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
