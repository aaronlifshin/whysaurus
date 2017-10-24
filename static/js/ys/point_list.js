import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import PointCard from './point';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import { gql, graphql } from 'react-apollo';

function* evidenceEdges(edges) {
  for (let edge of edges) {
    if (edge) {
      yield List(edge.node.supportingPoints ? edge.node.supportingPoints.edges : [])
      yield List(edge.node.counterPoints ? edge.node.counterPoints.edges : [])
    }
  }
}

export function evidenceRows(rowOfEdges) {
  let edges = List(evidenceEdges(rowOfEdges))
  return edges.first().zipAll(...edges.rest())
}

export function* edgeRows(rowOfEdges, depth = 0) {
  let row = List(rowOfEdges);
  if (row && !row.isEmpty()) {
    yield row.map(edge => Map(edge).set('depth', depth))
    for (let r of evidenceRows(row)) {
      for (let s of edgeRows(List(r), depth + 1)) {
	yield s
      }
    }
  }
}

class PointList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {points: dummyPoints, expandedIndex: {}}
    this.isPointExpanded = this.isPointExpanded.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.renderPointCard = this.renderPointCard.bind(this);
    this.renderPointRow = this.renderPointRow.bind(this);
    this.loadCurrentPagePoint = this.loadCurrentPagePoint.bind(this);
  }

  isPointExpanded(point) {
    return this.state.expandedIndex[point.key]
  }

  handleSeeEvidence(point) {
    const i = this.state.expandedIndex
    i[point.key] = true
    this.setState({expandedIndex: i})
    console.log("see evidence for ", point.key)
    let pointList = this
    this.loadPoint({url: point.url}, true, function(loadedPoint) {
        // TODO: the following code relies on the fact that `point` is
        // literally the same instance of Point that is in pointList.state.points
        // This is a dangerous assumption! We need proper state management...
        point.supportingPoints = loadedPoint.supportingPoints
        point.counterPoints = loadedPoint.counterPoints
        pointList.setState({points: pointList.state.points})
    })
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.key] = false
    this.setState({expandedIndex: i})
    console.log("hide evidence for ", point.key)
  }

  renderPointCard(pointContext, index) {
    let point = pointContext.point.node
    if (point) {
      return <div className="span5" key={point.key}>
        <PointCard point={point}
                   evidenceType={pointContext.evidenceType}
                   handleSeeEvidence={this.handleSeeEvidence} handleHideEvidence={this.handleHideEvidence}
                   expanded={this.state.expandedIndex[point.key]}/>
    </div>
    } else {
      return <div className="span5" key={index}></div>
    }
  }

  renderPointRow(row, rowIndex) {
    return <div className="row-fluid" key={rowIndex} style={{marginLeft: `${row.depth}em`}}>
      {this.renderPointCard(row.pointContexts[0], 0)}
      {row.pointContexts.slice(1).map(this.renderPointCard)}
    </div>
  }

  * zipEvidence(supportingPoints, counterPoints) {
    // zip together the lists leaving nils in place when the lists are different lengths  
    let l = Math.max(supportingPoints.length, counterPoints.length)
    for (var i = 0; i < l; i++) {
      yield [{evidenceType: EvidenceType.SUPPORT, point: supportingPoints[i].node},
             {evidenceType: EvidenceType.OPPOSE, point: counterPoints[i].node}]
    }
  }

  // pointsRows takes a list of point contexts that should appear in the same row and
  // returns a list of row rendering objects containing the given point contexts and
  // their expanded subpoints.
  // Each row rendering object contains depth context information and a list of
  // points that should be rendered in the same row.
  // Each point context contains the point and information like whether it appears in a
  // supporting or opposing list


  // TODO: rewrite points rows to deal directly with nodes and edges. I think we can drop pointContexts entirely?


  
  * pointsRows(rowCoresidentPointContexts, depth = 0) {
    yield {depth: depth, pointContexts: rowCoresidentPointContexts}
    for (let pointContext of rowCoresidentPointContexts) {
      if (pointContext.point && pointContext.point.node) {
	let point = pointContext.point.node
	console.log(point)
	let support = point.supportingPoints ? point.supportingPoints.edges : []
	let counter = point.counterPoints ? point.counterPoints.edges : []
	console.log(support)
	console.log(counter)
        for (let pointContexts of this.zipEvidence(support, counter)){
          for (let row of this.pointsRows(pointContexts, depth + 1)) {
            yield row
          }
        }
      }
    }
  }

  // return row rendering objects containing lists of Points and depth context information
  // each row will become a row in the grid system
  * pointsByRowAndColumn() {
    for (let row of this.pointsRows([{evidenceType: EvidenceType.ROOT,
                                      point: this.props.data.points.edges[0]}])){
      yield row
    }
    // yield {pointContexts: [{evidenceType: EvidenceType.ROOT,
    //                         point: this.state.points[1]}]}
  }

  * evidenceEdges(edges) {
    for (let edge of edges) {
      if (edge) {
	yield List(edge.node.supportingPoints ? edge.node.supportingPoints.edges : [])
	yield List(edge.node.counterPoints ? edge.node.counterPoints.edges : [])
      }
    }
  }

  evidenceRows(edges) {
    console.log("ev rows")
    console.log(prettyI(List(this.evidenceEdges(edges))))
    let evidenceEdges = List(this.evidenceEdges(edges))
    console.log("TURNS INTO")
    console.log(prettyI(evidenceEdges.first().zipAll(...evidenceEdges.rest())))
    console.log("fuz bang")
    return evidenceEdges.first().zipAll(...evidenceEdges.rest())
  }

  * edgeRows(row, depth = 0) {
    if (row && !row.isEmpty()) {
      yield row.map(edge => List([Map(edge).set('depth': depth)]))
      for (let r of this.evidenceRows(row)) {
	for (let s of this.edgeRows(List(r), depth + 1)) {
	  yield s
	}
      }
    }
  }
  
  * edgesByRowAndColumn() {
    console.log("bacon")
    for (let row of this.edgeRows(List(this.props.data.points.edges))) {
      console.log("fish")
      console.log(prettyI(row))
      yield row
    }
  }

  loadCurrentPagePoint(e){
    let pointList = this;
    console.log("load")
    // TODO: templateData is a global - that should change!
    this.loadPoint({url: templateData.url}, false, function(point) {
        pointList.setState({points: [point]})
    })
  }

  loadPoint(point, loadEvidence, onSuccess){
    $.ajax({
      	url: `/api/point/${point.url}`,
      	data: {evidence: loadEvidence},
      	success: onSuccess,
      	error: function(data) {
          console.log("error!!!!")
      	},
      });
  }

  // TODO:) WHY IS THIS RETURNING LISTS OF LISTS?!?!

  render(){
    if (this.props.loading) {
      return <div>Loading!</div>
    } else if (!this.props.data.points) {
      return <div>Loading points...</div>
    } else {
      console.log(this.props.data.points)
      // return <div>{JSON.stringify(this.props.data.points.edges)}</div>
      return <div className="row">
        <div className="span12">
        {JSON.stringify([...this.edgesByRowAndColumn()])}
        </div>
      </div>
    }
  }
}
      // .map(this.renderPointRow)
//        <button onClick={this.loadCurrentPagePoint}>Load current page point data</button>

const cards = <PointList/>;

export function PostList({data: {loading, points}}) {
  console.log("BAR")
  console.log(loading)
  console.log(points)
  if (loading) {
    return <div>Loading</div>;
  } else {
    return (
      <div>
        <ul>
          {points.map(point =>
            <li key={point.title}>
              {point.title}
              ({point.upVotes} votes)
            </li>
          )}
        </ul>
      </div>
    );
  }
}

export const getPoints = gql`{
  points(first: 1) {
    edges {
      node {
        title,
        upVotes,
        supportingPoints { edges { node { title, upVotes }, relevance } },
        counterPoints { edges { node { title, upVotes }, relevance } }
      }
    }
  }
}`;

export const PointListWithPoints = graphql(getPoints)(PointList);


