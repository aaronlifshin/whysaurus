import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';
import * as schema from './schema';

class Home extends React.Component {
  render(){
    return <div>Home Page!!</div>
  }
}

export const HomePage = graphql(schema.HomePage)(Home);
