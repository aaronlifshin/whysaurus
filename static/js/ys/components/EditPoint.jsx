import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import * as schema from '../schema';
import { graphql, compose } from 'react-apollo';
import TitleText from './TitleText'

const EditTitleForm = ( props ) => {
  return (
    <Form onSubmit={props.onSubmit}
          defaultValues={{title: props.point.title}}
          validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="editPointTextForm">
          <TitleText onClick={props.onClick} id="editPointTextField"/>
          <button onClick={props.onClick} className="buttonUX2" type="submit">Save</button>
        </form>
      )}
    </Form>
  );
}


class EditPointComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {saving: false}
    this.handleClickSave = this.handleClickSave.bind(this);
    this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  // TODO: this simple function is also defined in the PointCard component - can/should it be declared in a single place somehow?
  handleClickNoProp(e) {
    e.stopPropagation();
  }

  get point() {
    return this.props.point;
  }

  handleClickSave(values, e, formApi) {
    values.url = this.point.url
    this.setState({saving: true})
    this.props.mutate({
      variables: values
    })
    // this component will be replaced after save, so we don't need to update state
  }

  render(){
    const score = this.point.pointValue;
    if (this.state.saving) {
      return <div><img id="spinnerImage" className="spinnerPointSubmitButtonPosition" src="/static/img/ajax-loader.gif"/>Saving...</div>;
    } else {
      return <div>
        <span>
        <EditTitleForm onClick={this.handleClickNoProp} onSubmit={this.handleClickSave} point={this.point} countedValue={this.point.title}/>
        </span>
        <button onClick={this.props.onCancel} type="cancel" className="cancelButton">Cancel</button>
      </div>;
    }
  }
}

export default compose(
  graphql(schema.EditPointQuery),
)(EditPointComponent)
