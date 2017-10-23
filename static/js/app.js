import React from 'react';
import ReactDOM from 'react-dom';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");


import { gql, graphql, ApolloClient, ApolloProvider } from 'react-apollo';

const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("support"),
    OPPOSE: Symbol("oppose")
});

function Byline(props){
  return <span><a href={props.point.creatorURL}>@{props.point.creatorName}</a> and {props.point.numUsersContributed} others</span>
}

function CommentCount(props){
  return <span><i className="fa fa-comment-o"></i>{props.point.numComments}</span>
}

function ShareIcon(props){
  return <i className="fa fa-share-alt"></i>
}

function SupportingCount(props){
  return <span><i className="fa fa-level-up"></i>{props.point.supportedCount}</span>
}

function Point(props){
  const score = (props.point.upVotes || 0) - (props.point.downVotes || 0)
  return <span>{props.point.title}<b>{score > 0 && "+"}{score}</b></span>
}

class EvidenceLink extends React.Component {
  constructor(props) {
    super(props)
    this.handleClickSee = this.handleClickSee.bind(this);
    this.handleClickHide = this.handleClickHide.bind(this);
  }

  handleClickSee(e) {
    console.log("see");
    this.props.onSee && this.props.onSee()
  }

  handleClickHide(e) {
    console.log("hide");
    this.props.onHide && this.props.onHide()
  }

  render(){
    if (this.props.point.numSupporting > 0 || this.props.point.numCounter > 0) {
      if (this.props.expanded) {
        return <a onClick={this.handleClickHide}>Hide Evidence</a>
      } else {
        return <a onClick={this.handleClickSee}>See Evidence</a>
      }
    } else {
      return <span>No Evidence</span>
    }
  }
}

class AgreeDisagree extends React.Component {
  constructor(props) {
    super(props);
    // This binding is necessary to make `this` work in the callback
    this.handleClickAgree = this.handleClickAgree.bind(this);
    this.handleClickDisagree = this.handleClickDisagree.bind(this);
  }

  handleClickAgree() {
    console.log("agree");
  }

  handleClickDisagree() {
    console.log("disagree");
  }

  render(){
    return <span>
      <a onClick={this.handleClickAgree}>Agree</a>
      <a onClick={this.handleClickDisagree}>Disagree</a>
    </span>
    }

}

function More(){
  return <span>More</span>
}

class PointCard extends React.Component {
  constructor(props) {
    super(props)
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.state = {point: props.point}
  }

  handleSeeEvidence() {
    console.log("see evidence");
    this.props.handleSeeEvidence && this.props.handleSeeEvidence(this.props.point)
  }

  handleHideEvidence() {
    console.log("hide evidence");
    this.props.handleHideEvidence && this.props.handleHideEvidence(this.props.point)
  }

  evidenceTypeClass() {
    switch (this.props.evidenceType){
      case EvidenceType.ROOT:
        return "root"
      case EvidenceType.SUPPORT:
        return "support"
      case EvidenceType.OPPOSE:
        return "oppose"
      default:
        return ""
    }
  }

  render(){
    const point = this.state.point
    let classes = `point-card row-fluid ${this.evidenceTypeClass()}`
    return <div className={classes}>
      <div className="span9">
        <div className="row-fluid">
          <div className="span12">
            <Byline point={point}/>
            <CommentCount point={point}/>
            <ShareIcon point={point}/>
            <SupportingCount point={point}/>
          </div>
        </div>
        <div className="row-fluid">
          <div className="span12">
            <Point point={point}/>
          </div>
        </div>
        <div className="row-fluid">
          <div className="span12">
            <EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} expanded={this.props.expanded}/>
            <AgreeDisagree point={point}/>
            <More point={point}/>
          </div>
        </div>
      </div>
      <div className="span3">img</div>
    </div>
  }
}

const dummyPoints = [
  {
    key: 1,
    title: "I am the very model of a modern major general - I understand dynamics and my movement is perpetual",
    numSupporting: 1,
    numCounter: 0,
    upVotes: 48,
    downVotes: 6,
    sources: [],
    supportingPoints: [{
      key: 3,
      title: "I am in fact a general",
      numSupporting: 1,
      numCounter: 1,
      upVotes: 14,
      downVotes: 3,
      sources: [],
      supportingPoints: [],
      counterPoints: [{
        key: 5,
        title: "I do general stuff",
        numSupporting: 0,
        numCounter: 0,
        upVotes: 14,
        downVotes: 3,
        sources: [],
        supportingPoints: [],
        counterPoints: [],
        creatorName: "Trav",
        creatorURL: "http://trav.com",
        numUsersContributed: 12,
        numComments: 2
      }],
      creatorName: "Trav",
      creatorURL: "http://trav.com",
      numUsersContributed: 12,
      numComments: 2
    }],
    counterPoints: [{
      key: 4,
      title: "You aren't a great model",
      numSupporting: 0,
      numCounter: 0,
      upVotes: 40,
      downVotes: 100,
      sources: [],
      supportingPoints: [],
      counterPoints: [],
      creatorName: "Trav",
      creatorURL: "http://trav.com",
      numUsersContributed: 1,
      numComments: 1
    }],
    creatorName: "Trav",
    creatorURL: "http://trav.com",
    numUsersContributed: 3,
    numComments: 4
  },
  {
    key: 2,
    title: "Bacon is the greatest",
    numSupporting: 0,
    numCounter: 0,
    upVotes: 450,
    downVotes: 30,
    sources: [],
    supportingPoints: [],
    counterPoints: [],
    creatorName: "Bakedude",
    creatorURL: "http://bake.com",
    numUsersContributed: 2,
    numComments: 4,
    numSupported: 2,
    imageURL: ""
  }
]

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

const cards = <PointList/>

function PostList({data: {loading, points}}) {
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

const getPoints = gql`{
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

const PointListWithPoints = graphql(getPoints)(PointList);


const client = new ApolloClient({});

let templateData = document.getElementById('config') ? document.getElementById('config').dataset : {}
ReactDOM.render(
  <ApolloProvider client={client}><PointListWithPoints/></ApolloProvider>,
  document.getElementById('root')
);
