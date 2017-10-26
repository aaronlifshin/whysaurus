import React from 'react';
import ReactDOM from 'react-dom';


export const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("support"),
    COUNTER: Symbol("counter")
});

function Byline(props){
  return <span><a href={props.point.authorURL}>@{props.point.authorName}</a></span>
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

  get point() {
    return this.props.point;
  }

  hasEvidence() {
    return this.point.numSupporting > 0 || this.point.numCounter > 0;
  }

  hasExpandedEvidence() {
    return this.point.supportingPoints.edges.length > 0 || this.point.counterPoints.edges.length > 0
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
    if (this.hasEvidence()) {
      if (this.props) {
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
  }

  get point() {
    return this.props.point || this.props.edge.node;
  }

  get evidenceType() {
    return this.props.edge ? this.props.edge.evidenceType : null
  }

  handleSeeEvidence() {
    console.log("see evidence");
    this.props.handleSeeEvidence && this.props.handleSeeEvidence(this.point)
  }

  handleHideEvidence() {
    console.log("hide evidence");
    this.props.handleHideEvidence && this.props.handleHideEvidence(this.point)
  }

  evidenceTypeClass() {
    switch (this.evidenceType){
      case EvidenceType.ROOT:
        return "root"
      case EvidenceType.SUPPORT:
        return "support"
      case EvidenceType.COUNTER:
        return "counter"
      default:
        return ""
    }
  }

  render(){
    const point = this.point
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
      <div className="span3"><img src={point.imageURL} alt="an image"></img></div>
    </div>
  }
}

export {PointCard};
