import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import { PointList } from './PointList';
import Spinner from './Spinner'

const searchResultsDefaultPageSize = 10;
const SearchResultPointList = graphql(schema.FullClaimSearch, {
  options: ({pointsPerPage, q}) => ({variables: {q: q, limit: pointsPerPage || searchResultsDefaultPageSize}}),
  props: ({ownProps: {pointsPerPage, q}, data: { loading, fullClaimSearch = {}, fetchMore}}) => ({
    q: q,
    loading: loading,
    points: fullClaimSearch.points,
    hasMore: fullClaimSearch.hasMore,
    infiniteScroll: true,
    loadMorePoints: () => {
      return fetchMore({
        query: schema.FullClaimSearch,
        variables: {q: q, cursor: fullClaimSearch.cursor, limit: pointsPerPage || searchResultsDefaultPageSize},
        updateQuery: (previousResult, { fetchMoreResult }) => {
          fetchMoreResult.fullClaimSearch.points = [...previousResult.fullClaimSearch.points, ...fetchMoreResult.fullClaimSearch.points]
          return fetchMoreResult
        }
      })
    }
  })

})(PointList)

class SearchResults extends React.Component {
  render() {
    return <SearchResultPointList q={this.props.q}/>
  }
}

export default SearchResults
