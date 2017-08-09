import React from 'react';
import ReactDOM from 'react-dom';


function Byline(){
  return <span>@fixme and N others</span>
}

function CommentCount(){
  return <span>[]3</span>
}

function SupportingCount(){
  return <span>^4</span>
  
}

function Point(props){
  const score = (props.point.upVotes || 0) - (props.point.downVotes || 0)
  return <span>{props.point.title}<b>{score > 0 && "+"}{score}</b></span>
}

function EvidenceLink(){
  return <span>See Evidence</span>
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
      <button onClick={this.handleClickAgree}>Agree</button>
      <button onClick={this.handleClickDisagree}>Disagree</button>
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
        counterPoints: []
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
