import React from 'react'
import MediaQuery from 'react-responsive';
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'

// For Responsive
// TODO : move to config.js (also declared in home.js, and QuickCreateClaim.jsx)
const extraSmallScreenThreshold = 640;

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

  // TODO
  // replace <span className="">Pub.</span> with <span className="fa fa-edit"></span>
  // and figure out why it breaks when browser window expands width
  submitButtonLabel = () => {
    return <span>
        <MediaQuery minWidth={extraSmallScreenThreshold}>
          Publish
        </MediaQuery>
        <MediaQuery maxWidth={extraSmallScreenThreshold}>
          <span className="">Pub.</span>
        </MediaQuery> 
      </span>      
  }
  
  submitButton = () => {
    if (this.state.submitting) {
      return <span>Adding your point...</span>;
    } else {
      return <button onClick={this.props.onClick}className="buttonUX2 buttonUX2Blue buttonUX2RespIcon homePageNewPointCallButton pull-right" type="submit">{this.submitButtonLabel()}</button>;
    }
  }

  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="mainPageClaimCreationForm">
            <div className="mainPageClaimCreationFormFieldBlock">
              <TitleText id="newPointTextField" className="titleTextField" placeholder='Make a claim, eg "Dogs are better than cats."' />
            </div>
            <div className="mainPageClaimCreationFormButtonBlock">
              {this.submitButton()}
            </div>
          </form>
      )}
    </Form>;
  }
}
