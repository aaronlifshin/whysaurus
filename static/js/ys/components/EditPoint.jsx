import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import * as schema from '../schema';
import { graphql, compose } from 'react-apollo';
import TitleText from './TitleText'

const EditTitleForm = ({point, onSubmit, onClick}) => {
  return (
    <Form onSubmit={onSubmit}
          defaultValues={{title: point.title}}
          validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="editPointTextForm">
          <TitleText onClick={onClick} id="editPointTextField" className="titleTextField"/>
          <button onClick={onClick} className="buttonUX2" type="submit">Save</button>
        </form>
      )}
    </Form>
  );
}


class EditPointComponent extends React.Component {
  state = {saving: false}

  get point() {
    return this.props.point;
  }

  handleClickNoProp = (e) => {
    e.stopPropagation();
  }

  handleClickSave = (values, e, formApi) => {
    values.url = this.point.url
    this.setState({saving: true})
    this.props.mutate({
      variables: values
    }).then(null, (err) => this.setState({saving: false}))
  }

  render(){
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
