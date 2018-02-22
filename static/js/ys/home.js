import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql, compose } from 'react-apollo';
import { PointList } from './point_list';
import * as schema from './schema';
import { Form, Text } from 'react-form';
import { Carousel } from 'react-responsive-carousel';
import MediaQuery from 'react-responsive';

class QuickCreate extends React.Component {
  constructor(props) {
    super(props);
    this.state = {charsLeft: props.titleMaxCharacterCount};
    this.handleChange = this.handleChange.bind(this);
    this.submit = this.submit.bind(this);
    this.validateTitle = this.validateTitle.bind(this);
    this.errorValidator = this.errorValidator.bind(this);
  }

  handleChange(text) {
    this.setState({
      charsLeft: this.props.titleMaxCharacterCount - text.length
    });
  }

  submit(values, e, formApi){
    this.setState({submitting: true});
    this.props.onSubmit(values).then(
      (val) => {
        this.setState({submitting: false});
        formApi.resetAll();
      },
      (err) => {
        this.setState({submitting: false});
      });
  }

  validateTitle(title){
    if (!title || title.trim() === '') {
      return 'Point text is required.';
    } else if (title.length > this.props.titleMaxCharacterCount){
      return 'Point text too long.';
    } else {
      return null;
    }
  }

  errorValidator(values) {
    return {
      title: this.validateTitle(values.title)
    };
  }

  submitButton(){
    if (this.state.submitting) {
      return <span>Adding your point...</span>;
    } else {
      return <button onClick={this.props.onClick} className="buttonUX2" type="submit">Save</button>;
    }
  }

  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}
                 validateError={this.errorValidator}
                 dontValidateOnMount={true}>
      { formApi => (
          <form onSubmit={formApi.submitForm} className="editPointTextForm">
            <Text onChange={this.handleChange} field="title" id="editPointTextField" />
            {this.submitButton()}
            <p>{formApi.errors.title}</p>
          <p classes={this.state.charsLeft < 0 ? 'overMaxChars' : ''}>{this.state.charsLeft}</p>
          </form>
      )}
    </Form>;
  }
}

QuickCreate.defaultProps = {
  titleMaxCharacterCount: 200
};


class Home extends React.Component {

  constructor(props) {
    super(props);
    this.createNewPoint = this.createNewPoint.bind(this);
  }

  createNewPoint(pointData) {
    if (this.props.CurrentUserQuery.currentUser){
      return this.props.mutate({
        variables: pointData,
        update: (proxy, {data: {newPoint: { point }}}) => {
          const data = proxy.readQuery({ query: schema.HomePage});
          data.homePage.newPoints.unshift(point);
          proxy.writeQuery({query: schema.HomePage, data: data});
        }
      });
    } else {
      $("#loginDialog").modal("show");
      return Promise.reject("User not logged in");
    }
  }

  illustrations(){
    const singleColumnThreshold = 960;
    return <div className="row" id="explanationRowHomepage">
      <MediaQuery minWidth={singleColumnThreshold}>
        <div className="explanationsCentered">
          <div className="explanationBlock">
            <div className="explanationTextCentered">
                Make Arguments<br/><strong>Point-by-Point</strong>
            </div>
            <img className="explanationImageCentered" src="/static/img/homepage_illustration1_smaller.png"/>
          </div>
          <div className="explanationBlock">
            <div className="explanationTextCentered lessWidth">
              <strong>Rate and improve</strong> Points collaboratively
            </div>
            <img className="explanationImageCentered" src="/static/img/homepage_illustration2_smaller.png"/>
          </div>
          <div className="explanationBlock">
            <div className="explanationTextCentered lessWidth">
                <strong>Re-use</strong> Points to build new Arguments
            </div>
            <img className="explanationImageCentered" src="/static/img/homepage_illustration3_smaller.png"/>
          </div>
        </div>
      </MediaQuery>
      <MediaQuery maxWidth={singleColumnThreshold}>
      <Carousel showThumbs={false} showStatus={false} showIndicators={false}>
          <div>
            <img src="/static/img/homepage_illustration1_smaller.png"/>
            <p className="legend">Make Arguments<br/><strong>Point-by-Point</strong></p>
          </div>
          <div>
            <img src="/static/img/homepage_illustration2_smaller.png"/>
            <p className="legend"><strong>Rate and improve</strong> Points collaboratively</p>
          </div>
          <div>
            <img src="/static/img/homepage_illustration3_smaller.png"/>
            <p className="legend"><strong>Re-use</strong> Points to build new Arguments</p>
          </div>
        </Carousel>
      </MediaQuery>
    </div>;
  }

  render(){
    let homePage = this.props.data.homePage;
    let featuredPoint = homePage && homePage.featuredPoint;
    let newPoints = homePage && homePage.newPoints;
    let editorsPicks = homePage && homePage.editorsPicks;
    return <div>
      {this.illustrations()}
      <h3>Make an Argument You Want to Prove</h3>
      <QuickCreate onSubmit={this.createNewPoint}/>
      <h3>Featured Point:</h3>
      {featuredPoint && <PointList point={featuredPoint}/>}
      <h3>New Points:</h3>
      {newPoints && <PointList points={newPoints}/>}
      <h3>Editor's Picks:</h3>
      {editorsPicks && <PointList points={editorsPicks}/>}
    </div>;
  }
}

export const HomePage = compose(
  graphql(schema.CurrentUserQuery, {name: 'CurrentUserQuery'}),
  graphql(schema.HomePage),
  graphql(schema.NewPoint)
)(Home);