from google.appengine.ext import ndb

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.point import Point as PointModel
from models.whysaurususer import WhysaurusUser

class Point(NdbObjectType):
    class Meta:
        model = PointModel
        interfaces = (relay.Node,)

    id = graphene.NonNull(graphene.ID)
    def resolve_id(self, info):
        return self.url

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
class ExpandPoint(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, url):
        point, pointRoot = PointModel.getCurrentByUrl(url)
        return ExpandPoint(point=point)


class PointInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    parentURL = graphene.String()
    linkType = graphene.String()
    content = graphene.String()
    summaryText = graphene.String()
    imageURL = graphene.String()
    imageAuthor = graphene.String()
    imageDescription = graphene.String()
    sourceURLs = graphene.List(graphene.String)
    sourceNames = graphene.List(graphene.String)

class AddEvidence(graphene.Mutation):
    class Arguments:
        point_data = PointInput(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, point_data):
        oldPoint, oldPointRoot = PointModel.getCurrentByUrl(point_data.parentURL)
        newPoint, newLinkPoint = PointModel.addSupportingPoint(
            oldPointRoot=oldPointRoot,
            title=point_data.title,
            content=point_data.content,
            summaryText=point_data.summaryText,
            user=info.context.current_user,
            linkType=point_data.linkType,
            imageURL=point_data.imageURL,
            imageAuthor=point_data.imageAuthor,
            imageDescription=point_data.imageDescription,
            sourcesURLs=point_data.sourceURLs,
            sourcesNames=point_data.sourceNames
        )

        return AddEvidence(point=newPoint)

class Query(graphene.ObjectType):
    points = NdbConnectionField(Point)

    def resolve_points(self, info, **args):
        return PointModel.query()

    point = graphene.Field(Point, url=graphene.String())

    def resolve_point(self, info, **args):
        point, pointRoot = PointModel.getCurrentByUrl(args['url'])
        return point

class Mutation(graphene.ObjectType):
    expand_point = ExpandPoint.Field()
    add_evidence = AddEvidence.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


# test with:
# curl localhost:8081/graphql -d 'query GetPoints {
#   points {
#     title, upVotes, supportingPoints
#   }
# }'


# mutation AddEvidence {
#   addEvidence(pointData: {title: "bacon is fly", content: "bacon is fly", summaryText: "bacon is the flyest"}) {
#     point {
#       title
#     }
#   }
#}
