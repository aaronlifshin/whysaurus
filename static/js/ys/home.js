import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';
import { PointList } from './point_list';
import * as schema from './schema';

class Home extends React.Component {
  render(){
    let homePage = this.props.data.homePage;
    let featuredPoint = homePage && homePage.featuredPoint;
    let newPoints = homePage && homePage.newPoints;
    let editorsPicks = homePage && homePage.editorsPicks;
    return <div><h1>Home Page</h1>
      <h3>Featured Point:</h3>
      {featuredPoint && <PointList point={featuredPoint}/>}
      <h3>New Points:</h3>
      {newPoints && <PointList points={newPoints}/>}
      <h3>Editor's Picks:</h3>
      {editorsPicks && <PointList points={editorsPicks}/>}
      </div>
  }
}

export const HomePage = graphql(schema.HomePage)(Home);
