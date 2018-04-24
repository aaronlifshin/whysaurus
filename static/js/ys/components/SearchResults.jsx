import React from 'react';
import ReactDOM from 'react-dom';
import { graphql, compose, withApollo } from 'react-apollo';
import gql from 'graphql-tag';

export class SearchResults extends React.Component {
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    console.log("searchResults: componentDidMount()");
  }

  render() {
    return (
      <div>THIS IS THE SEARCH RESULTS AREA</div>
    )
  }
}

