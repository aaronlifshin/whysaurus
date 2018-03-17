import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'

export default class QuickCreateClaim extends React.Component {
  state = {submitting: false}

  submit = (values, e, formApi) => {
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

  submitButton = () => {
    if (this.state.submitting) {
      return <span>Adding your point...</span>;
    } else {
      return <button onClick={this.props.onClick} className="buttonUX2 buttonUX2Blue  homePageNewPointCallButton pull-right" type="submit">Publish</button>;
    }
  }

  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="mainPageClaimCreationForm">
            <TitleText id="newPointTextField" className="titleTextField" placeholder='Make a claim, eg "Dogs are better than cats."' />
            <div className="claimTextButtonsArea">
              {this.submitButton()}
            </div>
          </form>
      )}
    </Form>;
  }
}
