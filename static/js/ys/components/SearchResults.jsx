import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import Spinner from './Spinner'


class SearchResults extends React.Component {
  render() {
    const results = this.props.data.search
    return <div>{results && results.map((point, i) => <div key={i}>{point.title}</div>)}</div>
  }
}

export default graphql(schema.Search)(SearchResults)
