import logging
import pprint
from google.appengine.ext import ndb
import time

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from models.comment import Comment as CommentModel
from models.point import Point as PointModel
from models.point import PointRoot as PointRootModel
from models.point import Link as LinkModel
from models.point import FeaturedPoint
from models.uservote import RelevanceVote as RelevanceVoteModel
from models.source import Source as SourceModel
from models.whysaurususer import WhysaurusUser

class User(NdbObjectType):
    class Meta:
        model = WhysaurusUser

    admin = graphene.Boolean()
    def resolve_admin(self, info):
        return self.isAdmin

    hasConfirmedTermsAndConditions = graphene.Boolean()
    def resolve_hasConfirmedTermsAndConditions(self, info):
        return self.hasConfirmedTermsAndConditions

    recentlyViewed = graphene.List(lambda: Point)
    def resolve_recentlyViewed(self, info):
        return self.getRecentlyViewed()

class Source(NdbObjectType):
    class Meta:
        model = SourceModel

    id = graphene.NonNull(graphene.ID)
    def resolve_id(self, info):
        return self.key.urlsafe()

class Comment(NdbObjectType):
    class Meta:
        model = CommentModel

    id = graphene.NonNull(graphene.ID)
    def resolve_id(self, info):
        return self.key.urlsafe()

    parentID = graphene.ID()
    def resolve_parentID(self, info):
        return self.parentComment and self.parentComment.urlsafe()

class CommentInput(graphene.InputObjectType):
    pointID = graphene.String(required=True)
    text = graphene.String(required=True)
    parentCommentID = graphene.String()

class NewComment(graphene.Mutation):
    class Arguments:
        comment_data = CommentInput(required=True)

    comment = graphene.Field(Comment)

    def mutate(self, info, comment_data):
        comment = CommentModel.create(comment_data.text, info.context.current_user, PointRootModel.getByUrlsafe(comment_data.pointID), comment_data.parentCommentID)
        return NewComment(comment=comment)

class ArchiveComment(graphene.Mutation):
    class Arguments:
        pointID = graphene.String(required=True)
        commentID = graphene.String(required=True)

    numArchived = graphene.Int()

    def mutate(self, info, pointID, commentID):
        user = info.context.current_user
        if user and user.isAdmin:

            pointRoot = PointRootModel.getByUrlsafe(pointID)
            numArchived = pointRoot.archiveComments(commentID)
            return ArchiveComment(numArchived=numArchived)

class PointRoot(NdbObjectType):
    class Meta:
        model = PointRootModel

    numComments = graphene.Int()
    def resolve_numComments(self, info):
        return self.numComments

class Point(NdbObjectType):
    class Meta:
        model = PointModel
        interfaces = (relay.Node,)

    id = graphene.NonNull(graphene.ID)
    def resolve_id(self, info):
        return self.rootURLsafe

    root = graphene.Field(PointRoot)
    def resolve_root(self, info):
        return PointRootModel.getByUrlsafe(self.rootURLsafe)

    numSupporting = graphene.Int()
    def resolve_numSupporting(self, info):
        return self.numSupporting

    numCounter = graphene.Int()
    def resolve_numCounter(self, info):
        return self.numCounter

    pointValue = graphene.Int()
    def resolve_pointValue(self, info):
        return self.pointValueCached

    pointValueRaw = graphene.Int()
    def resolve_pointValueRaw(self, info):
        return self.pointValue

    fullPointImage = graphene.String()
    def resolve_fullPointImage(self, info):
        return self.fullPointImage

    sources = graphene.List(Source)
    def resolve_sources(self, info):
        return self.getSources()

    # numContributors = graphene.Int()
    # def resolve_numContributors(self, info):
    #     return self.numUsersContributed

    numUsersContributed = graphene.Int()
    def resolve_numUsersContributed(self, info):
        return self.numUsersContributed

    supportedCount = graphene.Int()
    def resolve_supportedCount(self, info):
        # TODO: need to get a link to the point root and then get supportedCount from that
        return 42

    engagementScore = graphene.Int()
    def resolve_engagementScore(self, info):
        return self.engagementScoreCached

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
        self._linkedPoints = self._linkedPoints or self.getAllLinkedPoints(info.context.current_user)

        points = self._linkedPoints[0]
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'supporting'
        return sorted((points or []), key=lambda x: -x.sortScore)

    counterPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_counterPoints(self, info, **args):
        self._linkedPoints = self._linkedPoints or self.getAllLinkedPoints(info.context.current_user)

        points = self._linkedPoints[1]
        if points:
            for point in points:
                point.parent = self
                point.link_type = 'counter'
        return sorted((points or []), key=lambda x: -x.sortScore)

    # a list of the most relevant supporting and counter points
    # introduced for single column views
    relevantPoints = relay.ConnectionField(lambda: SubPointConnection)
    def resolve_relevantPoints(self, info, **args):
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
        return sorted((supportingPoints or []) + (counterPoints or []), key=lambda point: -point.sortScore)


class Link(graphene.ObjectType):
    voteCount = graphene.Int()
    type = graphene.String()
    relevance = graphene.Float()
    sortScore = graphene.Float()
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
            return Link(type=self.node.link_type, sortScore=self.node._linkInfo.sortScore(self.node), relevance=self.node._linkInfo.rating, childURLsafe=self.node._linkInfo.root.urlsafe(), parentURLsafe=self.node.parent.rootURLsafe, relevanceVote=self.node.myVoteValue, voteCount=self.node._linkInfo.voteCount)

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

class LinkPoint(graphene.Mutation):
    class Arguments:
        parentURL = graphene.String(required=True)
        linkType = graphene.String(required=True)
        url = graphene.String(required=True)

    parent = graphene.Field(Point)
    point = graphene.Field(Point)

    newEdges = relay.ConnectionField(SubPointConnection)
    def resolve_newEdges(self, info, **args):
        return [self.point]

    def mutate(self, info, url, parentURL, linkType):
        supportingPoint, supportingPointRoot = PointModel.getCurrentByUrl(url)
        oldPoint, oldPointRoot = PointModel.getCurrentByUrl(parentURL)
        user = info.context.current_user
        if user:
            # NOTE: ported this over from handlers/linkpoint.py, don't totally understand it all
            # This code is if the vote existed before and the point was unlinked, and now
            # it is being re-linked
            voteCount, rating, myVote = RelevanceVoteModel.getExistingVoteNumbers(
                oldPointRoot.key, supportingPointRoot.key, linkType, user)
            supportingPoint._relevanceVote = myVote
            newLink = [{'pointRoot':supportingPointRoot,
                        'pointCurrentVersion':supportingPoint,
                        'linkType':linkType,
                        'voteCount': voteCount,
                        'fRating':rating}
            ]
            newVersion = oldPoint.update(
                pointsToLink=newLink,
                user=user
            )
            user.addRelevanceVote(
                oldPointRoot.key.urlsafe(),
                supportingPointRoot.key.urlsafe(), linkType, 100)

            # get my vote for this point, to render it in the linkPoint template
            supportingPoint.addVote(user)

            # these two are in service of the SubPointConnection logic - we should find a way to DRY this up
            supportingPoint.parent = newVersion
            supportingPoint.link_type = linkType

            return LinkPoint(parent=newVersion, point=supportingPoint)
        else:
            raise Exception("User not logged in.")


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

class NewPoint(graphene.Mutation):
    class Arguments:
        point_data = PointInput(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, point_data):
        newPoint, newPointRoot = PointModel.create(
            title=point_data.title,
            content=point_data.content,
            summaryText=point_data.summaryText,
            user=info.context.current_user,
            imageURL=point_data.imageURL,
            imageAuthor=point_data.imageAuthor,
            imageDescription=point_data.imageDescription
        )

        return NewPoint(point=newPoint)

class EditPointInput(graphene.InputObjectType):
    url = graphene.String(required=True)
    title = graphene.String()
    imageDescription = graphene.String()
    imageURL = graphene.String()

class EditPoint(graphene.Mutation):
    class Arguments:
        point_data = EditPointInput(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, point_data):
        point, pointRoot = PointModel.getCurrentByUrl(point_data.url)
        newPointVersion = point.update(user=info.context.current_user,
                                       newTitle=(point_data.title or point.title),
                                       imageURL=point_data.imageURL or point.imageURL,
                                       imageDescription=point_data.imageDescription or point.imageDescription,
        )
        return EditPoint(point=newPointVersion)

class AddSource(graphene.Mutation):
    class Arguments:
        pointID = graphene.String(required=True)
        url = graphene.String(required=True)
        name = graphene.String()

    point = graphene.Field(Point)

    def mutate(self, info, pointID, url, name=None):
        point, pointRoot = PointModel.getCurrentByRootKey(pointID)
        newPointVersion = point.update(user=info.context.current_user,
                                       sourcesToAdd=[SourceModel(parent=point.key, url=url, name=name)])
        return AddSource(point=newPointVersion)

class DeleteSource(graphene.Mutation):
    class Arguments:
        pointID = graphene.String(required=True)
        id = graphene.String(required=True)

    point = graphene.Field(Point)

    def mutate(self, info, pointID, id):
        point, pointRoot = PointModel.getCurrentByRootKey(pointID)
        newPointVersion = point.update(user=info.context.current_user,
                                       sourceKeysToRemove=[id])
        return AddSource(point=newPointVersion)

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
                    point.updateBacklinkedSorts(pointRoot)
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

class Delete(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)

    url = graphene.String()

    def mutate(self, info, url):
        user = info.context.current_user
        point, point_root = PointModel.getCurrentByUrl(url)
        result, msg = point_root.delete(user)
        if result:
            return Delete(url=url)
        else:
            raise Exception(str('delete failed: ' + msg))

class Unlink(graphene.Mutation):
    class Arguments:
        parentURL = graphene.String(required=True)
        url = graphene.String(required=True)
        linkType = graphene.String(required=True)

    parentURL = graphene.String()
    url = graphene.String()

    def mutate(self, info, parentURL, url, linkType):
        user = info.context.current_user
        point, point_root = PointModel.getCurrentByUrl(parentURL)
        new_version = point.unlink(url, linkType, user)
        if new_version:
            return Unlink(parentURL=parentURL, url=url)
        else:
            raise Exception(str('unlink failed:'))

class SetEditorsPick(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    point = graphene.Field(Point)
    point_root = graphene.Field(PointRoot)

    def mutate(self, info, id):
        user = info.context.current_user
        point, point_root = PointModel.getCurrentByRootKey(id)
        if user.isAdmin:
            if point_root.updateEditorsPick(True, int(-time.time())):
                return SetEditorsPick(point=point, point_root=point_root)
            else:
                raise Exception(str('set editors pick failed:'))
        else:
            raise Exception(str('non admin user tried to set editors pick'))

class MakeFeatured(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    point = graphene.Field(Point)
    point_root = graphene.Field(PointRoot)

    def mutate(self, info, id):
        user = info.context.current_user
        point, point_root = PointModel.getCurrentByRootKey(id)
        if user.isAdmin:
            if FeaturedPoint.setFeatured(point_root.key):
                return MakeFeatured(point=point, point_root=point_root)
            else:
                raise Exception(str('make featured failed:'))
        else:
            raise Exception(str('non admin user tried to set featured point'))


class AcceptTerms(graphene.Mutation):
    class Arguments:
        userUrl = graphene.String(required=True)
        
    success = graphene.Boolean()
    
    def mutate(self, info, userUrl):
        user = info.context.current_user
        if not user:
            raise Exception("User Not Logged In")
        
        if user.url != userUrl:
            raise Exception("Invalid User Url: Mismatches Current User")
        
        raise Exception('Test! Accepting Terms Here!')
        
        user.setTermsAccepted()

        return AcceptTerms(success=True)


class RelevanceVote(graphene.Mutation):
    class Arguments:
        linkType = graphene.String(required=True)
        url = graphene.String(required=True)
        parentRootURLsafe = graphene.String(required=True)
        rootURLsafe = graphene.String(required=True)
        vote = graphene.Int(required=True)

    point = graphene.Field(Point)
    parentPoint = graphene.Field(Point)
    link = graphene.Field(Link)

    def mutate(self, info, linkType, url, parentRootURLsafe, rootURLsafe, vote):
        user = info.context.current_user
        point, pointRoot = PointModel.getCurrentByUrl(url)
        if point:
            if user:
                pp, ppr = PointModel.getCurrentByRootKey(parentRootURLsafe)

                result, newRelevance, newVoteCount = user.addRelevanceVote(parentRootURLsafe, rootURLsafe, linkType, vote)
                if result:
                    return RelevanceVote(point=point, parentPoint=pp, link=Link(type=linkType, relevance=newRelevance, sortScore=LinkModel.calcSortScore(newRelevance, point.pointValueCached), relevanceVote=vote, voteCount=newVoteCount, parentURLsafe=parentRootURLsafe, childURLsafe=rootURLsafe))
                else:
                    raise Exception(str('vote failed: ' + str(vote)))
            else:
                raise Exception(str('user not defined ' +  str(user)))
        else:
            raise Exception(str('point not defined ' +  str(point)))

class PagedPoints(graphene.ObjectType):
    cursor = graphene.String()
    points = graphene.List(Point)
    hasMore = graphene.Boolean()

class HomePage(graphene.ObjectType):
    featuredPoint = graphene.Field(Point)
    def resolve_featuredPoint(self, info, **args):
        return FeaturedPoint.getFeaturedPoint()

    newPoints = graphene.List(Point)
    def resolve_newPoints(self, info, **args):
        return PointRootModel.getRecentCurrentPoints(info.context.current_user)

    editorsPicks = graphene.List(Point)
    def resolve_editorsPicks(self, info, **args):
        return PointRootModel.getEditorsPicks(info.context.current_user)

class Query(graphene.ObjectType):
    points = NdbConnectionField(Point)
    def resolve_points(self, info, **args):
        return PointModel.query()

    point = graphene.Field(Point, url=graphene.String())
    def resolve_point(self, info, **args):
        point, pointRoot = PointModel.getCurrentByUrl(args['url'])
        return point

    comments = graphene.List(Comment, pointID=graphene.String(required=True), showArchived=graphene.Boolean())
    def resolve_comments(self, info, pointID, showArchived=False):
        point, point_root = PointModel.getCurrentByRootKey(pointID)
        comments = point_root.getComments()
        if showArchived:
            comments = comments + point_root.getArchivedComments()
        return comments

    homePage = graphene.Field(HomePage)
    def resolve_homePage(self, info):
        return HomePage()

    newPoints = graphene.Field(PagedPoints, cursor=graphene.String(), limit=graphene.Int())
    def resolve_newPoints(self, info, **args):
        results, nextCursor, more = PointRootModel.getRecentCurrentPointsPage(user=info.context.current_user, cursor=args.get('cursor', None), limit=args.get('limit', 5))
        return PagedPoints(cursor=nextCursor.urlsafe(), points=results, hasMore=more)

    currentUser = graphene.Field(User)
    def resolve_currentUser(self, info):
        return info.context.current_user

    search = graphene.List(Point, query=graphene.String(required=True))
    def resolve_search(self, info, **args):
        searchResultsFuture = PointModel.search(
            user=info.context.current_user,
            searchTerms="\"" + (args['query'] or "") + "\""
        )
        searchResults = searchResultsFuture.get_result() if searchResultsFuture else []
        return searchResults

class Mutation(graphene.ObjectType):
    delete = Delete.Field()
    unlink = Unlink.Field()
    expand_point = ExpandPoint.Field()
    add_evidence = AddEvidence.Field()
    link_point = LinkPoint.Field()
    edit_point = EditPoint.Field()
    vote = Vote.Field()
    relevanceVote = RelevanceVote.Field()
    new_point = NewPoint.Field()
    new_comment = NewComment.Field()
    archive_comment = ArchiveComment.Field()
    add_source = AddSource.Field()
    delete_source = DeleteSource.Field()
    set_editors_pick = SetEditorsPick.Field()
    make_featured = MakeFeatured.Field()
    accept_terms = AcceptTerms.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


# test with:
# curl localhost:8081/graphql -d 'query GetPoints {
#   points {
#     title, upVotes, supportingPoints
#   }
# }'
