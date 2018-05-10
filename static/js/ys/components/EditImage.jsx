import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import * as schema from '../schema';
import { graphql, compose } from 'react-apollo';
import TitleText from './TitleText'
import Spinner from './Spinner'
import { CloseLinkX } from './common'
import ImagePicker from './ImagePicker';
import config from '../config'

class EditImageForm  extends React.Component {

  state = {}

  render() {
    const {point, onSubmit, onClick, heightClass} = this.props
  return (
    <Form onSubmit={onSubmit}
          defaultValues={{imageURL: point.imageURL, imageDescription: point.imageDescription}}
          validate={values => ({imageDescription: validations.validateCaption(values.imageDescription)})}>
      { ({submitForm, values: {imageDescription, imageURL}, validationFailures}) => (
        <form onSubmit={submitForm} id="form1" className="editPointTextForm">
          {imageURL && <img src={config.cdn.baseURL + imageURL}/>}
          <ImagePicker field="imageURL"
            onUploaded={(file) => {
              this.setState({imageURL: file.key})
            }}
            onTransformed={(result) => {
              console.log("Saved transformed versions of image:")
              console.log(result)
            }}
            />
            <div className="claimCreationFormFieldBlock">
              <Text field="imageDescription" onClick={onClick} onSubmit={submitForm}/>
            </div>
            <div className="claimCreationFormButtonBlock">
              <button onClick={onClick} className="buttonUX2 createClaimFormButton" type="submit">Update Image</button>
            </div>

        </form>
      )}
    </Form>
  );
  }
}


class EditImageComponent extends React.Component {
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
    this.props.save(values).
      then((result) => this.setState({saving: false}),
           (err) => this.setState({saving: false}))
  }

  // TODO: this algorithm is a sketch, might not be ideal
  getEditTextFormHeightClass(title){
    if (title.length > 160 )
      return "sixLines";
    if (title.length > 130 )
      return "fiveLines";
    if (title.length > 100 )
      return "fourLines";
    if (title.length > 65 )
      return "threeLines";
    else
      return "twoLines";
  }

  render(){
    let editClaimTextClasses = `claimEditArea pointCardPaddingH editClaimText`
    if (this.state.saving) {
      return <div className={editClaimTextClasses}>
        <span className="claimEditAreaSavingFeedback"><Spinner /><span className="spinnerLabel">Saving...</span></span>
      </div>;
    } else {
      return <div className={editClaimTextClasses}>
        <EditImageForm onClick={this.handleClickNoProp} onSubmit={this.handleClickSave} point={this.point} countedValue={this.point.title} heightClass={this.getEditTextFormHeightClass(this.point.title)}/>
      </div>;
    }
  }
}

export default compose(
  graphql(schema.EditPointQuery, {
    props: ({mutate}) => ({
      save: (values) => mutate({
        variables: values
      })
    })
  }),
)(EditImageComponent)
