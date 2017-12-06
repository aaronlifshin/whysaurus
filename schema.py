import logging
from google.appengine.ext import ndb

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.point import Point as PointModel
from models.source import Source as SourceModel
from models.whysaurususer import WhysaurusUser

# ideally we could use NdbObjectType here too, but I was running into funny errors.
class User(graphene.ObjectType):
    url = graphene.String()

class Source(NdbObjectType):
    class Meta:
        model = SourceModel

class Point(NdbObjectType):
    class Meta:
        model = PointModel
        interfaces = (relay.Node,)

    id = graphene.NonNull(graphene.ID)
    def resolve_id(self, info):
        return self.rootURLsafe

    numSupporting = graphene.Int()
    def resolve_numSupporting(self, info):
        return self.numSupporting

    numCounter = graphene.Int()
    def resolve_numCounter(self, info):
        return self.numCounter

    fullPointImage = graphene.String()
    def resolve_fullPointImage(self, info):
        return self.fullPointImage

    sources = graphene.List(Source)
    def resolve_sources(self, info):
        return self.getSources()

    numComments = graphene.Int()
    def resolve_numComments(self, info):
        # TODO: need to get a link to the point root and then get numComments from that
        return 42

    supportedCount = graphene.Int()
    def resolve_supportedCount(self, info):
        # TODO: need to get a link to the point root and then get supportedCount from that
        return 42

    rootURLsafe = graphene.String()
    def resolve_rootURLsafe(self, info):
        return self.rootURLsafe

    currentUserVote = graphene.Int()
    def resolve_currentUserVote(self, info):
        return info.context.current_user.getVoteValue(self.key.parent())

    supportingPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_supportingPoints(self, info, **args):
        points = self.getLinkedPoints("supporting", None)
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'supporting'
        return points or []

    counterPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_counterPoints(self, info, **args):
        points = self.getLinkedPoints("counter", None)
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'counter'
        return points or []


class Link(graphene.ObjectType):
    voteCount = graphene.Int()
    type = graphene.String()
    relevance = graphene.Float()
    parentURLsafe = graphene.String()
    childURLsafe = graphene.String()

    id = graphene.NonNull(graphene.ID)
    # make id synthetic to support generating it from either SubPointConnection or RelevanceVote
    def resolve_id(self, info):
        return str(self.childURLsafe + self.type + self.parentURLsafe)

class SubPointConnection(relay.Connection):
    class Meta:
        node = Point

    class Edge:
        link = graphene.Field(Link)
        def resolve_link(self, info):
            return Link(type=self.node.link_type, relevance=self.node._linkInfo.rating, childURLsafe=self.node._linkInfo.root.urlsafe(), parentURLsafe=self.node.parent.rootURLsafe)

        relevance = graphene.Float()
        def resolve_relevance(self, info, **args):
            return self.node._linkInfo.rating

        relevanceVoteCount = graphene.Int()
        def resolve_relevanceVoteCount(self, info):
            return self.node.relevanceVoteCount

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

class EditPointInput(graphene.InputObjectType):
    url = graphene.String(required=True)
    title = graphene.String()

class EditPoint(graphene.Mutation):
    class Arguments:
        point_data = EditPointInput(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, point_data):
        point, pointRoot = PointModel.getCurrentByUrl(point_data.url)
        newPointVersion = point.update(user=info.context.current_user, newTitle=point_data.title)
        return EditPoint(point=newPointVersion)

class Vote(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)
        vote = graphene.Int(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, url, vote):
        user = info.context.current_user
        point, pointRoot = PointModel.getCurrentByUrl(url)
        if point:
            if user:
                vote = user.addVote(point, vote)
                if vote:
                    return Vote(point=point)
                else:
                    raise Exception(str('vote failed: ' + str(vote)))
            else:
                raise Exception(str('user not defined ' +  str(user)))
        else:
            raise Exception(str('point not defined ' +  str(point)))

class RelevanceVote(graphene.Mutation):
    class Arguments:
        linkType = graphene.String(required=True)
        url = graphene.String(required=True)
        parentRootURLsafe = graphene.String(required=True)
        rootURLsafe = graphene.String(required=True)
        vote = graphene.Int(required=True)

    point = graphene.Field(Point)
    link = graphene.Field(Link)

    def mutate(self, info, linkType, url, parentRootURLsafe, rootURLsafe, vote):
        user = info.context.current_user
        point, pointRoot = PointModel.getCurrentByUrl(url)
        if point:
            if user:
                result, newRelevance, newVoteCount = user.addRelevanceVote(parentRootURLsafe, rootURLsafe, linkType, vote)
                if result:
                    return RelevanceVote(point=point, link=Link(type=linkType, relevance=newRelevance, parentURLsafe=parentRootURLsafe, childURLsafe=rootURLsafe))
                else:
                    raise Exception(str('vote failed: ' + str(vote)))
            else:
                raise Exception(str('user not defined ' +  str(user)))
        else:
            raise Exception(str('point not defined ' +  str(point)))

class Query(graphene.ObjectType):
    points = NdbConnectionField(Point)
    def resolve_points(self, info, **args):
        return PointModel.query()

    point = graphene.Field(Point, url=graphene.String())
    def resolve_point(self, info, **args):
        point, pointRoot = PointModel.getCurrentByUrl(args['url'])
        return point

    currentUser = graphene.Field(User)
    def resolve_currentUser(self, info):
        user = info.context.current_user
        if (user):
            return User(url=user.url)

class Mutation(graphene.ObjectType):
    expand_point = ExpandPoint.Field()
    add_evidence = AddEvidence.Field()
    edit_point = EditPoint.Field()
    vote = Vote.Field()
    relevanceVote = RelevanceVote.Field()


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
