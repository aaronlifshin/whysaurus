import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import {GetPoint, EvidenceType, PointCard, ExpandedPointCard, Byline, newPointCard, expandedPointFieldsFragment} from './point';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';

class PointList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {expandedIndex: {}}
    this.isPointExpanded = this.isPointExpanded.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
  }

  isPointExpanded(point) {
    return this.state.expandedIndex[point.url]
  }

  handleSeeEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = true
    this.setState({expandedIndex: i})
    console.log("see evidence for ", point.url)
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = false
    this.setState({expandedIndex: i})
    console.log("hide evidence for ", point.url)
  }

  renderPointCard(pointEdge, index) {
    return newPointCard(pointEdge,
                        {index: index,
                         expandedIndex: this.state.expandedIndex,
                         handleSeeEvidence: this.handleSeeEvidence,
                         handleHideEvidence:this.handleHideEvidence});
  }

  renderPointCards(data) {
    if (data.point) {
      return this.renderPointCard({node: data.point})
    } else if (data.points) {
      return this.renderPointCard(data.points.edges[0])
    } else {
        return <div>Could not find data.point or data.points, please check your query.</div>
    }
  }

  render(){
    console.log("render")
    if (this.props.data && this.props.data.loading) {
      return <div>Loading!</div>
    } else if (!(this.props.data.points || this.props.data.point)) {
      return <div>Loading points...</div>
    } else {
	  // FOR INIFINITE WIDTH VERSION: remove .span12 from #infiniteOrFiniteWidth	
	  // FOR FINITE WIDTH VERSION: add .span12 from #infiniteOrFiniteWidth		  
      return <div className="row pointStream">
        <div id="infiniteOrFiniteWidth" className=""> 
	{this.renderPointCards(this.props.data)}

        </div>
      </div>
    }
  }
}

// const GetPoints = gql`
// ${expandedPointFieldsFragment}
// query GetPoints {
//   points(first: 1) {
//     edges {
//       node {
//         ...pointFields
//         ...evidenceFields
//       }
//     }
//   }
// }`;


// return the "whysaurus url" for this page
function url(){
  let parts = window.location.pathname.split("/");
  return parts.pop() || parts.pop(); // the || accounts for a trailing slash
}

// TODO: this doesn't work, but will need to for, eg, front page point lists
// export const PointListWithPoints = graphql(GetPoints)(PointList);

export const PointListWithPoint = graphql(GetPoint, {options: {variables: {url: url()}}})(PointList);
