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
    this.props.onSubmit(values);
    formApi.resetAll();
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

  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}
                 validateError={this.errorValidator}
                 dontValidateOnMount={true}>
      { formApi => (
          <form onSubmit={formApi.submitForm} className="editPointTextForm">
            <Text onClick={props.onClick} onChange={this.handleChange} field="title" id="editPointTextField" />
            <button onClick={props.onClick} className="buttonUX2" type="submit">Save</button>
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
    this.props.mutate({
      variables: pointData,
      update: (proxy, {data: {newPoint: { point }}}) => {
        const data = proxy.readQuery({ query: schema.HomePage})
        data.homePage.newPoints.unshift(point)
        proxy.writeQuery({query: schema.HomePage, data: data})
      }
    });
  }

  render(){
    let homePage = this.props.data.homePage;
    let featuredPoint = homePage && homePage.featuredPoint;
    let newPoints = homePage && homePage.newPoints;
    let editorsPicks = homePage && homePage.editorsPicks;
    return <div><h1>Home Page</h1>
      <h3>Make an Argument You Want to Prove</h3>
      <QuickCreate onSubmit={this.createNewPoint}/>
      <h3>Featured Point:</h3>
      {featuredPoint && <PointList point={featuredPoint}/>}
      <h3>New Points:</h3>
      {newPoints && <PointList points={newPoints}/>}
      <h3>Editor's Picks:</h3>
      {editorsPicks && <PointList points={editorsPicks}/>}
      </div>
  }
}

export const HomePage = compose(
  graphql(schema.HomePage),
  graphql(schema.NewPoint)
)(Home);
