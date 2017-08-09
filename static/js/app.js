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

function EvidenceLink(props){
  if (props.point.numSupporting > 0 || props.point.numCounter > 0) {
    return <span>See Evidence</span>
  } else {
    return <span>No Evidence</span>
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

function PointCard(props){
  const point = props.point
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
          <EvidenceLink point={point}/>
          <AgreeDisagree point={point}/>
          <More point={point}/>
        </div>
      </div>
    </div>
    <div className="span3">img</div>
  </div>
}

class PointList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {points: [
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
        numSupported: 2
      }
    ]}
  }

  render(){
    return <div className="row">
      <div className="span12">
      {this.state.points.map((point) =>
        <PointCard point={point} key={point.key}/>
      )}
      </div>
    </div>
  }
}

const cards = <PointList/>

ReactDOM.render(
  cards,
  document.getElementById('root')
);
