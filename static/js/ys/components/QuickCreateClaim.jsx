import React from 'react'
import MediaQuery from 'react-responsive';
import config from '../config'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'
import Spinner from './Spinner'


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
  // replace <span className="">Add</span> with <span className="fa fa-edit"></span> for desired look
  // but this also makes the bug reappear:
  // when browser width goes from narrow to wide, errors are thrown and page is blank
  // (seems to work fine going from wide to narrow)
  // make work!
  submitButtonLabel = () => {
    return <span>
        <MediaQuery minWidth={config.extraSmallScreenThreshold}>
          Publish
        </MediaQuery>
        <MediaQuery maxWidth={config.extraSmallScreenThreshold}>
          <span className="">Add</span>
        </MediaQuery>
      </span>
  }

  submitButton = ({...rest}) => {
    if (this.state.submitting) {
      return <span className="quickCreateClaimFeedback">
        <Spinner /><span className="spinnerLabel">Adding your claim...</span>
      </span>;
    } else {
      return <button className="buttonUX2 buttonUX2Blue buttonUX2RespIcon createClaimFormButton" type="submit" {...rest}>{this.submitButtonLabel()}</button>;
    }
  }

  // TO DO: there is bug around validationFailures - its returning 0 when it shouldn't be
  //   for now, adding the condition (title.length > validations.titleMaxCharacterCount) to make the button disable when it should
  //   but really we should fix the bug
  //   see PR here: https://github.com/aaronlifshin/whysaurus/pull/82#pullrequestreview-111369929
  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { ({validationFailures, values: {title}, submitForm}) => (
          <form onSubmit={submitForm} id="mainPageClaimCreationForm">
            <div className="claimCreationFormFieldBlock">
              <TitleText id="newPointTextField" className="titleTextField" onSubmit={submitForm} placeholder='Make a claim, eg "Dogs are better than cats."' />
            </div>
            <div className="claimCreationFormButtonBlock">
              {this.submitButton({disabled: (!title || (title == "") || (title.length > validations.titleMaxCharacterCount) ) || (validationFailures > 0)})}
            </div>
          </form>
      )}
    </Form>;
  }
}
