import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import { PointCard } from './point';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';
import { GetPoint } from './schema.js';
import { withRouter } from 'react-router';

class PointListComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {expandedIndex: this.urlExpandedIndex()}
    this.isPointExpanded = this.isPointExpanded.bind(this);
  }

  get parentPoint() {
    return this.props.parentPoint;
  }

  isPointExpanded(point) {
    return !!this.state.expandedIndex[point.url]
  }

  expandedIndex2Param = (index) => {
    console.log(index)
    return JSON.stringify(Object.keys(index).filter(key => index[key]))
  }

  expandedParam2Index = (param) => {
    try {
      return param ? JSON.parse(param).reduce((i, k) => {i[k] = true; return i}, {}) : {}
    } catch (err) {
      console.log("Error parsing URL expanded index:")
      console.log(param)
      console.log(err)
      return {}
    }
  }

  urlExpandedIndex = (urlSearchParams) => {
    let params = urlSearchParams || new URLSearchParams(this.props.location.search)
    return this.expandedParam2Index(params.get("expanded"))
  }

  updateURLExpandedIndex = (urlSearchParams, updatedIndex) => {
    let params = urlSearchParams || new URLSearchParams(this.props.location.search)
    if (Object.entries(updatedIndex).length > 0) {
      params.set("expanded", this.expandedIndex2Param(updatedIndex))
    } else {
      params.delete("expanded")
    }
    const { location, history } = this.props
    history.push({path: location.pathname, search: params.toString()})
  }

  modifyStateAndURL = (point, indexModifier) => {
    let params = new URLSearchParams(this.props.location.search);
    let index = this.urlExpandedIndex()
    indexModifier(index)
    this.setState({expandedIndex: index})
    this.updateURLExpandedIndex(params, index)
  }

  handleSeeEvidence = (point) => {
    this.modifyStateAndURL(point, index => index[point.url] = true)
  }

  handleHideEvidence = (point) => {
    this.modifyStateAndURL(point, index => delete index[point.url])
  }

  renderPoint(point) {
    if (this.isPointExpanded(point)) {
      return <PointCard key={point.url} url={point.url} point={point} expanded={true}
                        parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onCollapse={() => this.handleHideEvidence(point)}/>
    } else {
      return <PointCard key={point.url} point={point} url={point.url} expanded={false}
                        parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onExpand={() => this.handleSeeEvidence(point)}/>
    }
  }

  renderEdge(edge) {
    if (this.isPointExpanded(edge.node)) {
      return <PointCard key={edge.node.url} point={edge.node} url={edge.node.url} expanded={true}
                        link={edge.link} parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onCollapse={() => this.handleHideEvidence(edge.node)}/>
    } else {
      return <PointCard key={edge.node.url} point={edge.node} url={edge.node.url} expanded={false}
                        link={edge.link} parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onExpand={() => this.handleSeeEvidence(edge.node)}/>
    }
  }

  render(){
    if (this.props.point) {
      return this.renderPoint(this.props.point);
    } else if (this.props.points) {
      return <div>
        {this.props.points.map((point, i) => this.renderPoint(point))}
      </div>
    } else if (this.props.loading || (this.props.data && this.props.data.loading)) {
      return <div><img id="spinnerImage" className="spinnerPointSubmitButtonPosition" src="/static/img/ajax-loader.gif"/>Loading!</div>
    } else if (this.props.data && this.props.data.point) {
      return this.renderPoint(this.props.data.point);
    } else if (this.props.edges) {
      return <div>
        {this.props.edges.map((edge, i) => this.renderEdge(edge))}
        </div>
    } else {
      return <div>dunno what to do...</div>
    }
  }
}
const PointList = withRouter(PointListComponent);

export {PointList};
export const PointListWithPoint = graphql(GetPoint)(PointList);
