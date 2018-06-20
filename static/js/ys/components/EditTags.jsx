import React from 'react'
import { graphql, compose } from 'react-apollo';
import { Form, Text } from 'react-form';

import { CloseLinkX } from './common'
import * as validations from '../validations';
import * as schema from '../schema';

class EditTagComponent extends React.Component {

  state = {saving: false}

  deleteTag = (id) => {
    this.setState({saving: true})
    console.log('Deleting Tag: ' + id + ' Point: ' + this.props.point.id)
    this.props.delete(this.props.point.id, id)
  }

  render() {
    if (this.state.saving) {
      return "saving..."
    } else {
      const {id, url, text} = this.props.tag
      return <div>
          <a className="tag" tabIndex="-1" target="_blank" href={url}>
             <span className="iconSourcesSmall">
              <span className="fas fa-book"></span>
            </span>
            <span className="tagLabel">{text || url}</span>
          </a>
          <a className="removeTagLink easierToClickOn" onClick={() => this.deleteTag(id)}><CloseLinkX/></a>
        </div>
    }
  }
}

const EditTag = compose(
  graphql(schema.DeleteTag, {
    props: ({mutate}) => ({
      delete: (pointID, id) => mutate({
        variables: {pointID, id}
      })
    })
  }),
)(EditTagComponent)

class EditTagsComponent extends React.Component {

  state = {saving: false}

  onSubmit = ({tagId}) => {
    this.setState({saving: true})
    console.log('Submitting Tag: ' + tagId)
    this.props.add(this.props.point.id, tagId).then(() => this.setState({saving: false}))
  }

  render(){
    const tags = this.props.point.tags
    let editTagsLabel = `${tags ? "Edit Tags" : "Add Tags"}`
    return <div className="row-fluid claimEditArea editTags ">
      <span className="claimEditAreaHeading">
        <span className="heading">{editTagsLabel}</span>
        <span className="editAreaClose"><a onClick={this.props.onCancel}><CloseLinkX/></a></span>
      </span>
      <div className="claimEditAreaNote hotTip">Select an existing tag: (Or send us feedback for new claims)</div>
      <div className="editTagsList">
        {tags && tags.map((tag, i) => <EditTag key={i} point={this.props.point} tag={tag}/>)}
      </div>
      <Form onSubmit={this.onSubmit}
            validate={values => ({tagId: validations.validateTagId(values.tagId)})}>
      {({errors, submitForm}) => <form onSubmit={submitForm}>
        <Text field="tagId" className="inputFieldUX2 inputFieldUX2multi" placeholder="tag"/>
        {errors && errors.tagId && <div className="error">{errors.tagId}</div>}
        {this.state.saving ? "saving..." : <button disabled={false} className="buttonUX2 pull-right" type="submit">Add Tag</button>}
       </form>}
      </Form>
    </div>
  }
}

export default compose(
  graphql(schema.AddTag, {
    props: ({mutate}) => ({
      add: (pointID, tagUrl) => mutate({
        variables: {pointID, tagUrl}
      })
    })
  })
)(EditTagsComponent)
