import React from 'react';
import ReactDOM from 'react-dom';


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

  render(){
    const point = this.state.point
    return <div className="row-fluid" style={{border: '1px gray solid'}}>
      <div className="span9">
        <div className="row">
          <div className="span9">
            <Byline point={point}/>
            <CommentCount point={point}/>
            <ShareIcon point={point}/>
            <SupportingCount point={point}/>
          </div>
        </div>
        <div className="row">
          <div className="span9">
            <Point point={point}/>
          </div>
        </div>
        <div className="row">
          <div className="span9">
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
    numSupporting: 10,
    numCounter: 5,
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
  }

  isPointExpanded(point) {
    return this.state.expandedIndex[point.key]
  }

  handleSeeEvidence(point) {
    const i = this.state.expandedIndex
    i[point.key] = true
    this.setState({expandedIndex: i})
    console.log("see evidence for ", point.key)
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.key] = false
    this.setState({expandedIndex: i})
    console.log("hide evidence for ", point.key)
  }

  renderPointCard(point, index, offset = 0) {
    let classes = "span5" //+ (offset > 0 ? ` offset${offset * 0.25}` : "")
    if (point) {
      return <div className={classes} key={point.key}>
        <PointCard point={point}
                   handleSeeEvidence={this.handleSeeEvidence} handleHideEvidence={this.handleHideEvidence}
                   expanded={this.state.expandedIndex[point.key]}/>
    </div>
    } else {
      return <div className={classes} key={index}></div>
    }
  }

  renderPointRow(row, rowIndex) {
    return <div className="row-fluid" key={rowIndex} style={{marginLeft: `${row.depth}em`}}>
      {this.renderPointCard(row.points[0], 0, row.depth)}
      {row.points.slice(1).map(this.renderPointCard)}
    </div>
  }

  * zipEvidence(supportingPoints, counterPoints) {
    // zip together the lists leaving nils in place when the lists are different lengths  
    let l = Math.max(supportingPoints.length, counterPoints.length)
    for (var i = 0; i < l; i++) {
      yield [supportingPoints[i], counterPoints[i]]
    }
  }

  // pointsRows takes a list of points that should appear in the same row and
  // returns a list of row rendering objects containing the given points and
  // their expanded subpoints.
  // Each row rendering object contains depth context information and a list of
  // points that should be rendered in the same row.
  * pointsRows(rowCoresidentPoints, depth = 0) {
    yield {depth: depth, points: rowCoresidentPoints}
    for (let point of rowCoresidentPoints) {
      if (point && this.isPointExpanded(point)) {
        for (let points of this.zipEvidence(point.supportingPoints, point.counterPoints)){
          for (let row of this.pointsRows(points, depth + 1)) {
            yield row
          }
        }
      }
    }
  }

  // return row rendering objects containing lists of Points and depth context information
  // each row will become a row in the grid system
  * pointsByRowAndColumn() {
    for (let row of this.pointsRows([this.state.points[0]])){
      yield row
    }
    yield {points: [this.state.points[1]]}
  }

  render(){
    return <div className="row">
      <div className="span12">

      {[...this.pointsByRowAndColumn()].map(this.renderPointRow)}
      </div>
    </div>
  }
}

const cards = <PointList/>

ReactDOM.render(
  cards,
  document.getElementById('root')
);
