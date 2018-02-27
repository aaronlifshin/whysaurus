import gql from 'graphql-tag';

export const CurrentUserQuery = gql`
query CurrentUser {
  currentUser { url }
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
  numComments,
  supportedCount,
  sources {url, name},
  rootURLsafe,
  currentUserVote
}
`

export const evidenceEdgesFragment = gql`
fragment evidenceEdges on SubPointConnection {
  edges { node { ...pointFields }, link { id, type, relevance, relevanceVote, parentURLsafe, childURLsafe }}
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

export const NewPoints = gql`
${pointFieldsFragment}
query HomePage {
  homePage {
    newPoints {
      ...pointFields
    }
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
