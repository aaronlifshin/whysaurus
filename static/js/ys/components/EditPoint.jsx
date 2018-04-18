import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import * as schema from '../schema';
import { graphql, compose } from 'react-apollo';
import TitleText from './TitleText'
import Spinner from './Spinner'
import CloseLinkX from './Point'


const EditTitleForm = ({point, onSubmit, onClick}) => {
  return (
    <Form onSubmit={onSubmit}
          defaultValues={{title: point.title}}
          validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="editPointTextForm">
          <div className="claimCreationFormFieldBlock">
            <TitleText onClick={onClick} id="editPointTextField" className="titleTextField" onSubmit={formApi.submitForm}/>
          </div>
          <div className="claimCreationFormButtonBlock">
            <button onClick={onClick} className="buttonUX2 createClaimFormButton" type="submit">Save</button>
          </div>            
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
    let editClaimTextClasses = `claimEditArea pointCardPaddingH editClaimText`
    if (this.state.saving) {
      return <div className={editClaimTextClasses}>
        <span className="claimEditAreaSavingFeedback"><Spinner /><span className="spinnerLabel">Saving...</span></span>
      </div>;
    } else {
      return <div className={editClaimTextClasses}>
        <span className="claimEditAreaHeading">
          <span className="heading">Edit Claim Text</span>
          <span className="editAreaClose"><a onClick={this.props.onCancel}><CloseLinkX/></a></span>
        </span>        
        <EditTitleForm onClick={this.handleClickNoProp} onSubmit={this.handleClickSave} point={this.point} countedValue={this.point.title}/>

        
      </div>;
    }
  }
}

export default compose(
  graphql(schema.EditPointQuery),
)(EditPointComponent)
