import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import * as schema from '../schema'
import { graphql, compose, withApollo } from 'react-apollo'
import gql from 'graphql-tag'
import { ApolloClient } from 'apollo-client'
import { PointList } from './PointList'

export class SearchResults extends React.Component {
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    console.log("searchResults: componentDidMount()")
  }

  points = ({results, searching}) => {
    if (searching) {
      return <div/>
    }
    else {  //Josh: show a point_list with the results
      // const items = results.map(res => <div key={res.id}>{res.url} || {res.title}</div>)
      // return (
      //   <div>
      //     <div>Search results for '{this.props.searchValue}':</div>
      //     <div>{items}</div>
      //   </div>
      // )
      return (
        <div className="evidenceBlockBoth evidenceBlockFirstColAlignment">
          <div>Search results for '{this.props.searchValue}':</div>
          <div className="evidenceList">
            <PointList points={results.html}/>
          </div>
        </div>
      )
    }
  }

  render() {
    return <div>this.props.match.params.q = {this.props.match.params.q}</div>     //this.points
  }
}

// export default graphql(schema.FullPointSearch, {
//   skip: (ownProps) => !ownProps.query || (ownProps.query == '')
// })(SearchResults)
