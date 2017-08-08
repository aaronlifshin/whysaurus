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

function Point(){
  return <span>I am the very model of a modern major general - I understand dynamics and my movement is perpetual <b>+42</b></span>
}

function EvidenceLink(){
  return <span>See Evidence</span>
}

function AgreeDisagree(){
  return <span>Agree Disagree</span>
}

function More(){
  return <span>More</span>
}

function PointCard(){
  return <div className="row">
    <div className="span9">
      <div className="row">
        <div className="span9">
          <Byline/>
          <CommentCount/>
          <SupportingCount/>
        </div>
      </div>
      <div className="row">
        <div className="span9">
          <Point/>
        </div>
      </div>
      <div className="row">
        <div className="span9">
          <EvidenceLink/>
          <AgreeDisagree/>
          <More/>
        </div>
      </div>
    </div>
    <div className="span3">img</div>
  </div>
}
const card = <PointCard/>

ReactDOM.render(
  card,
  document.getElementById('root')
);