import gql from 'graphql-tag';

export const CurrentUserQuery = gql`
query CurrentUser {
  currentUser { url, admin, role, recentlyViewed { id, url, title } }
}`

export const pointFieldsFragment = gql`
fragment pointFields on Point {
  id,
  url,
  title,
  authorName,
  authorURL,
  imageURL,
  fullPointImage,
  upVotes,
  downVotes,
  pointValue,
  numSupporting,
  numCounter,
  numUsersContributed,
  supportedCount,
  sources {url, name},
  rootURLsafe,
  currentUserVote,
  root {
    numComments
  }
}
`

export const evidenceEdgesFragment = gql`
fragment evidenceEdges on SubPointConnection {
  edges { node { ...pointFields }, link { id, type, relevance, relevanceVote, voteCount, parentURLsafe, childURLsafe }}
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
mutation EditPoint($url: String!, $title: String) {
  editPoint(pointData: {url: $url, title: $title}) {
    point {
      id,
      title,
      url
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

export const UnlinkPointMutation = gql`
mutation Unlink($parentURL: String!, $url: String!, $linkType: String!) {
  unlink(parentURL: $parentURL, url: $url, linkType: $linkType) {
    parentURL,
    url
  }
}
`

export const RelevanceVoteQuery = gql`
mutation RelevanceVote($linkType: String!, $parentRootURLsafe: String!, $rootURLsafe: String!, $url: String!, $vote: Int!) {
  relevanceVote(linkType: $linkType, rootURLsafe: $rootURLsafe, parentRootURLsafe: $parentRootURLsafe, url: $url, vote: $vote) {
    point {
      id
    }

    link {
      id,
      type,
      relevance,
      relevanceVote,
      voteCount,
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

const commentFieldsFragment = gql`
fragment commentFields on Comment {
  id
  text
  parentID
  level
}
`

export const Comments = gql`
${commentFieldsFragment}
query Comments($pointID: String) {
  comments(pointID: $pointID) {
    ...commentFields
  }
}
`


export const NewComment = gql`
mutation NewComment($pointID: String!, $text: String!, $parentCommentID: String) {
  newComment(commentData: {pointID: $pointID, text: $text, parentCommentID: $parentCommentID}) {
    comment {
      ...commentFields
    }
  }
}
`
