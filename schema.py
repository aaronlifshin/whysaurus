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

    pointValue = graphene.Int()
    def resolve_pointValue(self, info):
        return self.pointValue()

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
        if (info.context.current_user):
            return info.context.current_user.getVoteValue(self.key.parent())
        else:
            return 0

    # TODO: we call getAllLinkedPoints 3 times - find a way to cache that value

    supportingPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_supportingPoints(self, info, **args):
        if (('omitEvidence' in info.variable_values) and info.variable_values['omitEvidence']):
            return []
        self._linkedPoints = self._linkedPoints or self.getAllLinkedPoints(info.context.current_user)

        points = self._linkedPoints[0]
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'supporting'
        return points or []

    counterPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_counterPoints(self, info, **args):
        if (('omitEvidence' in info.variable_values) and info.variable_values['omitEvidence']):
            return []
        self._linkedPoints = self._linkedPoints or self.getAllLinkedPoints(info.context.current_user)

        points = self._linkedPoints[1]
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'counter'
        return points or []

    # a list of the most relevant supporting and counter points
    # introduced for single column views
    relevantPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_relevantPoints(self, info, **args):
        if (('omitEvidence' in info.variable_values) and info.variable_values['omitEvidence']):
            return []
        self._linkedPoints = self._linkedPoints or self.getAllLinkedPoints(info.context.current_user)

        supportingPoints, counterPoints = self._linkedPoints
        if supportingPoints:
            for point in supportingPoints:
                point.parent = self
                point.link_type = 'supporting'
        if counterPoints:
            for point in counterPoints:
                point.parent = self
                point.link_type = 'counter'
        # TODO: sort by relevance, or do a more efficient query that just returns the most relevant points
        return sorted((supportingPoints or []) + (counterPoints or []), key=lambda point: -point.relevance)


class Link(graphene.ObjectType):
    voteCount = graphene.Int()
    type = graphene.String()
    relevance = graphene.Float()
    relevanceVote = graphene.Int()
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
            return Link(type=self.node.link_type, relevance=self.node._linkInfo.rating, childURLsafe=self.node._linkInfo.root.urlsafe(), parentURLsafe=self.node.parent.rootURLsafe, relevanceVote=self.node.myVoteValue)

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

    parent = graphene.Field(Point)
    point = graphene.Field(Point)

    newEdges = relay.ConnectionField(SubPointConnection)
    def resolve_newEdges(self, info, **args):
        return [self.point]

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

        # these two are in service of the SubPointConnection logic - we should find a way to DRY this up
        newLinkPoint.parent = newPoint
        newLinkPoint.link_type = point_data.linkType

        return AddEvidence(point=newLinkPoint, parent=newPoint)

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
        parentURL = graphene.String()

    point = graphene.Field(Point)
    parentPoint = graphene.Field(Point)

    def mutate(self, info, url, vote, parentURL=None):
        user = info.context.current_user
        point, pointRoot = PointModel.getCurrentByUrl(url)
        if point:
            if user:
                voteResult = user.addVote(point, vote)
                if voteResult:
                    if parentURL:
                        pp, ppr = PointModel.getCurrentByUrl(parentURL)
                        return Vote(point=point, parentPoint=pp)
                    else:
                        return Vote(point=point, parentPoint=None)
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
                    return RelevanceVote(point=point, link=Link(type=linkType, relevance=newRelevance, relevanceVote=vote, parentURLsafe=parentRootURLsafe, childURLsafe=rootURLsafe))
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

    point = graphene.Field(Point, url=graphene.String(), omitEvidence=graphene.Boolean())
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
