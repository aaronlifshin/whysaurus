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
    return <div className="row">
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
    supportingPoints: [],
    counterPoints: [],
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
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.renderPointCard = this.renderPointCard.bind(this);

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

  renderPointCard(point) {
    return <PointCard point={point} key={point.key} 
                      handleSeeEvidence={this.handleSeeEvidence} handleHideEvidence={this.handleHideEvidence}
                      expanded={this.state.expandedIndex[point.key]}/>
  }

  render(){
    return <div className="row">
      <div className="span12">
      {this.state.points.map(this.renderPointCard)}
      </div>
    </div>
  }
}

const cards = <PointList/>

ReactDOM.render(
  cards,
  document.getElementById('root')
);
