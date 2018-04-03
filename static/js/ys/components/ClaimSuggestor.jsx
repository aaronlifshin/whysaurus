import React from 'react'
import PropTypes from 'prop-types'
import { compose, graphql } from 'react-apollo';
import * as schema from '../schema';

class ClaimSuggestor extends React.Component {
  static propTypes = {
    point: PropTypes.object,
    evidenceType: PropTypes.string,
    render: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props)
    this.invalidEvidenceURLs = new Set([props.point.url, ...this.evidence().map(claim => claim.url)])
  }

  evidence = () => {
    let connections = this.props.point[this.props.evidenceType == "supporting" ? "supportingPoints" : "counterPoints"]
    return connections ? connections.edges.map(edge => edge.node) : []
  }

  filterEvidenceCandidates = (claims) =>
    claims.filter(claim => !this.invalidEvidenceURLs.has(claim.url))

  suggestions = () => {
    const {user, query, searchResults, searching} = this.props
    if (query && (query != '')){
      if (!searching) {
        return this.filterEvidenceCandidates(searchResults)
      }
    } else if (user) {
      return this.filterEvidenceCandidates(user.recentlyViewed)
    }
  }

  render(){
    const {search, searching} = this.props.data || {}
    return (
      this.props.render({suggestions: this.suggestions(), searching: searching})
    )
  }
}

export default compose(
  graphql(schema.Search, {
    skip: (ownProps) => !ownProps.query || (ownProps.query == ''),
    props: ({ownProps, data: {loading, search, refetch}}) => ({
      searching: loading,
      searchResults: search,
      refetchSearch: refetch
    })
  }),
  graphql(schema.CurrentUserQuery, {
    props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
      userLoading: loading,
      user: currentUser,
      refetchUser: refetch
    })
  })
)(ClaimSuggestor)
