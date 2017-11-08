import React from 'react';
import ReactDOM from 'react-dom';
import { gql, graphql, compose } from 'react-apollo';


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
  return <i className="fa fa-share-alt"></i>;
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
    super(props);
    this.state = {expandedIndex: {}}
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.renderSubPointCard = this.renderSubPointCard.bind(this);
  }

  get point() {
    return this.props.point || this.props.edge.node;
  }

  get evidenceType() {
    return this.props.edge ? this.props.edge.evidenceType : null;
  }

  handleSeeEvidence(point=this.point) {
    const i = this.state.expandedIndex
    i[point.url] = true
    this.setState({expandedIndex: i})
    console.log("see pc evidence for " + point.url);
    // this.props.mutate({
    //   variables: { url: point.url }
    // })
    //   .then(({ data }) => {
    //     console.log('got data', data);
    //   }).catch((error) => {
    //     console.log('there was an error sending the query', error);
    //   });
    this.props.handleSeeEvidence && this.props.handleSeeEvidence(point);
  }

  handleHideEvidence(point=this.point) {
    const i = this.state.expandedIndex
    i[point.url] = false
    this.setState({expandedIndex: i})
    console.log("hide pc evidence for " + point.url);
    this.props.handleHideEvidence && this.props.handleHideEvidence(point);
  }

  expanded() {
    return this.state.expandedIndex[this.point.url]
  }

  evidenceTypeClass() {
    switch (this.evidenceType){
      case EvidenceType.ROOT:
        return "root";
      case EvidenceType.SUPPORT:
        return "support";
      case EvidenceType.COUNTER:
        return "counter";
      default:
        return "";
    }
  }

  renderSubPointCard(pointEdge, index){
    return newPointCard(pointEdge,
                        {index: index,
                         expandedIndex: this.state.expandedIndex,
                         handleSeeEvidence: this.handleSeeEvidence,
                         handleHideEvidence:this.handleHideEvidence});
  }

  render(){
    const point = this.point;
    console.log("rendering " + point.url)
    let classes = `point-card row-fluid ${this.evidenceTypeClass()}`;
    return <div>
      <div className={classes}>
        <div className="span9">
          <div className="row-fluid">
            <div className="span12">
              <Byline point={point}/>
              <CommentCount point={point}/>t
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
              <EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} expanded={this.expanded()}/>
              <AgreeDisagree point={point}/>
              <More point={point}/>
            </div>
          </div>
        </div>
        <div className="span3"><img src={point.imageURL} alt="an image"></img></div>
      </div>
      <div className="row-fluid">
      <div className="support span6">
      {this.expanded() && this.point.supportingPoints &&
       this.point.supportingPoints.edges.map(this.renderSubPointCard)}
      </div>
      <div className="counter span6">
      {this.expanded() && this.point.counterPoints &&
       this.point.counterPoints.edges.map(this.renderSubPointCard)}
    </div>
      </div>
    </div>;
  }
}

export function newPointCard(pointEdge, {index, expandedIndex, handleSeeEvidence, handleHideEvidence}) {
  let point = pointEdge.node;
  if (point) {
    if (!expandedIndex[point.url]) {
      console.log("point card for " + point.url);
      console.log(expandedIndex)
      return <div className="span5" key={point.url}>
        <CollapsedPointCard point={point}
          expandedIndex={expandedIndex}
          expanded={false}
          evidenceType={pointEdge.evidenceType}
          handleSeeEvidence={handleSeeEvidence}
          handleHideEvidence={handleHideEvidence}/>
        </div>
    } else {
      console.log("expanded point card for " + point.url);
      console.log(expandedIndex)
      return <div className="span5" key={point.url}>
        <ExpandedPointCard point={point}
            url={point.url}
            expandedIndex={expandedIndex}
            expanded={true}
            evidenceType={pointEdge.evidenceType}
            handleSeeEvidence={handleSeeEvidence}
            handleHideEvidence={handleHideEvidence}/>
        </div>;
    }
  } else {
    return <div className="span5" key={index}></div>;
  }
}

export const pointFieldsFragment = gql`
fragment pointFields on Point {
  id,
  url,
  title,
  authorName,
  authorURL,
  imageURL,
  upVotes,
  downVotes,
  numSupporting,
  numCounter,
  numComments,
  supportedCount
}
fragment evidenceFields on Point {
 supportingPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } },
 counterPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } }
}`

export const expandedPointFieldsFragment = gql`
${pointFieldsFragment}
fragment evidenceFields on Point {
 supportingPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } },
 counterPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } }
}`

export const GetPoint = gql`
${expandedPointFieldsFragment}
query Point($url: String) {
  point(url: $url) {
    ...pointFields,
    ...evidenceFields
 }
}`

export const ExpandPoint = gql`
${expandedPointFieldsFragment}
mutation ExpandPoint($url: String!) {
  expandPoint(url: $url) {
    point {
      id,
      ...evidenceFields
    }
  }
}`
export {PointCard};
export const ExpandedPointCard =   graphql(GetPoint)(PointCard)
export const CollapsedPointCard =   graphql(ExpandPoint)(PointCard)
