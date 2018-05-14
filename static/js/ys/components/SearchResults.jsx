import React from 'react'
import ReactDOM from 'react-dom'
import { graphql, compose, withApollo } from 'react-apollo'
import gql from 'graphql-tag'
import { ApolloClient } from 'apollo-client'
import HeaderSearch from './HeaderSearch'
import { PointList } from './PointList'

export class SearchResults extends React.Component {
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    console.log("searchResults: componentDidMount()")
  }

  //this is the render-props rendering function that'll get called from HeaderSearch's render()
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
            <PointList points={results}/>
          </div>
        </div>
      )
    }
  }

  render() {
    return (
      <HeaderSearch query={this.props.searchValue} render={this.points}/>
    )
  }
}

