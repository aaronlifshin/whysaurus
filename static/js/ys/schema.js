import gql from 'graphql-tag';

export const CurrentUserQuery = gql`
query CurrentUser {
  currentUser { url, admin, hasConfirmedTermsAndConditions, hasConfirmedHeaderWalkthrough, role, recentlyViewed { id, url, title } }
}`

export const pointFieldsFragment = gql`
fragment pointFields on Point {
  id,
  url,
  title,
  authorName,
  authorURL,
  creatorName,
  creatorURL,
  imageURL,
  imageDescription,
  fullPointImage,
  upVotes,
  downVotes,
  pointValue,
  numSupporting,
  numCounter,
  numUsersContributed,
  supportedCount,
  engagementScore,
  sources { id, url, name },
  tags { id, url, text },
  rootURLsafe,
  currentUserVote,
  root {
    numComments
  }
}
`

export const evidenceEdgesFragment = gql`
fragment evidenceEdges on SubPointConnection {
  edges { node { ...pointFields }, link { id, type, relevance, relevanceVote, voteCount, sortScore, parentURLsafe, childURLsafe }}
}`


export const expandedPointFieldsFragment = gql`
${pointFieldsFragment}
${evidenceEdgesFragment}
fragment evidenceFields on Point {
 supportingPoints { ...evidenceEdges },
 counterPoints { ...evidenceEdges },
 relevantPoints { ...evidenceEdges }
}`

export const EditPointQuery = gql`
mutation EditPoint($url: String!, $title: String, $imageDescription: String, $imageURL: String) {
  editPoint(pointData: {url: $url, title: $title, imageDescription: $imageDescription, imageURL: $imageURL}) {
    point {
      id,
      title,
      url,
      imageURL,
      imageDescription,
      fullPointImage
    }
  }
}
`

export const AddEvidenceQuery = gql`
${pointFieldsFragment}
${evidenceEdgesFragment}
mutation AddEvidence($title: String!, $linkType: String, $parentURL: String, $imageURL: String, $imageAuthor: String, $imageDescription: String, $sourceURLs: [String], $sourceNames: [String]) {
  addEvidence(pointData: {title: $title, content: $title, summaryText: $title, imageURL: $imageURL, imageAuthor: $imageAuthor, imageDescription: $imageDescription, sourceURLs: $sourceURLs, sourceNames: $sourceNames, linkType: $linkType, parentURL: $parentURL}) {
    newEdges { ...evidenceEdges }
    parent { id, numSupporting, numCounter }
  }
}
`

export const LinkPoint = gql`
${pointFieldsFragment}
${evidenceEdgesFragment}
mutation LinkPoint($parentURL: String!, $url: String!, $linkType: String!) {
  linkPoint(parentURL: $parentURL, linkType: $linkType, url: $url) {
    newEdges { ...evidenceEdges }
    parent { id, numSupporting, numCounter }
  }
}
`

export const VoteQuery = gql`
mutation Vote($url: String!, $vote: Int!, $parentURL: String) {
  vote(url: $url, vote: $vote, parentURL: $parentURL) {
    point {
      id
      pointValue
      upVotes
      downVotes
      currentUserVote
    }
    parentPoint {
      id
      pointValue
    }
  }
}
`

export const DeletePointMutation = gql`
mutation Delete($url: String!) {
  delete(url: $url) {
    url
  }
}
`

export const AddSource = gql`
mutation AddSource($pointID: String!, $url: String!, $name: String) {
  addSource(pointID: $pointID, url: $url, name: $name) {
    point {
      id
      sources { id, name, url }
    }
  }
}

`
export const DeleteSource = gql`
mutation DeleteSource($pointID: String!, $id: String!) {
  deleteSource(pointID: $pointID, id: $id) {
    point {
      id
      sources { id, name, url }
    }
  }
}
`

export const AddTag = gql`
mutation AddTag($pointID: String!, $tagUrl: String!) {
  addTag(pointID: $pointID, tagUrl: $tagUrl) {
    point {
      id
      tags { id, text, url }
    }
  }
}

`
export const DeleteTag = gql`
mutation DeleteTag($pointID: String!, $id: String!) {
  deleteTag(pointID: $pointID, id: $id) {
    point {
      id
      tags { id, text, url }
    }
  }
}
`

export const UnlinkPointMutation = gql`
mutation Unlink($parentURL: String!, $url: String!, $linkType: String!) {
  unlink(parentURL: $parentURL, url: $url, linkType: $linkType) {
    parentURL,
    url
  }
}
`

export const SetEditorsPick = gql`
mutation SetEditorsPick($id: String!) {
  setEditorsPick(id: $id) {
    point {
      id
    }
  }
}
`

export const MakeFeatured = gql`
mutation MakeFeatured($id: String!) {
  makeFeatured(id: $id) {
    point {
      id
    }
  }
}
`

export const RelevanceVoteQuery = gql`
mutation RelevanceVote($linkType: String!, $parentRootURLsafe: String!, $rootURLsafe: String!, $url: String!, $vote: Int!) {
  relevanceVote(linkType: $linkType, rootURLsafe: $rootURLsafe, parentRootURLsafe: $parentRootURLsafe, url: $url, vote: $vote) {
    point {
      id
    }

    parentPoint {
      id
      pointValue
    }

    link {
      id,
      type,
      relevance,
      relevanceVote,
      voteCount,
      sortScore,
      parentURLsafe,
      childURLsafe
    }
  }
}
`

export const GetPoint = gql`
${expandedPointFieldsFragment}
query Point($url: String) {
  point(url: $url) {
    ...pointFields,
    ...evidenceFields
 }
}`

export const GetCollapsedPoint = gql`
${pointFieldsFragment}
query Point($url: String) {
  point(url: $url) {
    ...pointFields
 }
}`

export const Search = gql`
query Search($query: String!) {
  search(query: $query) {
    id, url, title
  }
}`

export const FullClaimSearch = gql`
${pointFieldsFragment}
query FullClaimSearch($q: String!, $cursor: String, $limit: Int) {
  fullClaimSearch(q: $q, cursor: $cursor, limit: $limit) {
    cursor
    points {
      ...pointFields
    }
    hasMore
  }
}`

export const HomePage = gql`
${pointFieldsFragment}
query HomePage {
  homePage {
    featuredPoint {
      ...pointFields
    }
  }
}
`

export const EditorsPicks = gql`
${pointFieldsFragment}
query HomePage {
  homePage {
    editorsPicks {
      ...pointFields
    }
  }
}
`

export const NewPointsOne = gql`
${pointFieldsFragment}
query HomePage {
  homePage {
    newPoints {
      ...pointFields
    }
  }
}
`

export const NewPoints = gql`
${pointFieldsFragment}
query NewPoints($cursor: String, $limit: Int) {
  newPoints(cursor: $cursor, limit: $limit) {
    cursor
    points {
      ...pointFields
    }
    hasMore
  }
}
`

export const NewPoint = gql`
${pointFieldsFragment}
mutation NewPoint($title: String!, $imageURL: String, $imageAuthor: String, $imageDescription: String, $sourceURLs: [String], $sourceNames: [String]) {
  newPoint(pointData: {title: $title, content: $title, summaryText: $title, imageURL: $imageURL, imageAuthor: $imageAuthor, imageDescription: $imageDescription, sourceURLs: $sourceURLs, sourceNames: $sourceNames}) {
    point { ...pointFields }
  }
}
`

export const AcceptTerms = gql`
mutation AcceptTerms($userUrl: String!) {
  acceptTerms(userUrl: $userUrl) {
    success
  }
}
`

export const SetUserFlag = gql`
mutation SetUserFlag($userUrl: String!, $flag: String!, $value: Int!) {
  setUserFlag(userUrl: $userUrl, flag: $flag, value: $value) {
    success
  }
}
`

const commentFieldsFragment = gql`
fragment commentFields on Comment {
  id
  text
  parentID
  level
  date
  userName
  userUrl
  archived
}
`

export const Comments = gql`
${commentFieldsFragment}
query Comments($pointID: String!, $showArchived: Boolean) {
  comments(pointID: $pointID, showArchived: $showArchived) {
    comments {
      ...commentFields
    }
    archivedCount
  }
}
`

export const History = gql`
query History($url: String!) {
  history(url: $url) {
    point{
      version
      url
      title
      authorName
      authorURL
      dateEdited
      imageURL
      imageDescription
    }
    supportingPoints {
      url
      title
      version
    }
    counterPoints {
      url
      title
      version
    }
    sources {
      id
      url
      name
    }
  }
}
`

export const NewComment = gql`
${commentFieldsFragment}
mutation NewComment($pointID: String!, $text: String!, $parentCommentID: String) {
  newComment(commentData: {pointID: $pointID, text: $text, parentCommentID: $parentCommentID}) {
    comment {
      ...commentFields
    }
  }
}
`

export const ArchiveComment = gql`
mutation ArchiveComment($pointID: String!, $commentID: String!) {
  archiveComment(pointID: $pointID, commentID: $commentID) {
    numArchived
  }
}
`
