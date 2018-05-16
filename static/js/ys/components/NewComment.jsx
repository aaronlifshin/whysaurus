import React from 'react'
import MediaQuery from 'react-responsive';
import config from '../config'
import * as validations from '../validations';
import { Form, Text, TextArea } from 'react-form';
import Spinner from './Spinner'


export default class NewComment extends React.Component {
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
      return <span className="newCommentFeedback">
        <Spinner /><span className="spinnerLabel">Adding your comment...</span>
      </span>;
    } else {
      return <div>
        <button className="buttonUX2 newCommentPublishButton" type="submit" {...rest}>{this.submitButtonLabel()}</button>
        <button className="cancelButton cancelButtonNewComment" onClick={this.props.onCancel}>Cancel</button>
      </div>
    }
  }

  render(){
    let props = this.props;
    return <Form onSubmit={this.submit}>
      { ({validationFailures, values: {text}, submitForm}) => (
          <form onSubmit={submitForm} id="newCommentCreationForm">
            <div className="newCommentFormFieldBlock">
              <TextArea field="text" id="newCommentTextField" className="inputFieldUX2" placeholder='Suggest a clarification, or another way to improve this claim' />
            </div>
            <div className="newCommentFormButtonBlock">
              {this.submitButton({disabled: (!text || (text == ""))})}
            </div>
          </form>
      )}
    </Form>;
  }
}
