import React from 'react'
import PropTypes from 'prop-types'
import { Form, Text } from 'react-form';
import { graphql } from 'react-apollo';

import * as validations from '../validations';
import * as schema from '../schema';
import TitleText from './TitleText'
import ClaimSearch from './ClaimSearch'

// use onmousedown here to try to get in before blur hides the UI (see note in TitleText onBlur below)
// TODO: check in with Josh to see if we can come up with better "hide" conditions so we can avoid this
const ExistingClaimPicker = ({claims, onSelectClaim}) => <ul>
      {claims && claims.map((claim) => <li onMouseDown={e => onSelectClaim(claim, e)} key={claim.id}>
                            {claim.title}
                            </li>)}
      </ul>

class AddEvidenceForm extends React.Component {

  static propTypes = {
    addExistingClaim: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired
  }

  state = {titleTextFocused: false}

  selectExistingClaim = (claim) => {
    this.props.addExistingClaim(claim)
  }

  existingClaimPicker = (titleValue, searchResults, searching) => {
    if (this.state.titleTextFocused) {
      if (titleValue && (titleValue != '')){
        if (searching) {
          return <div>Searching...</div>
        } else {
          return <ExistingClaimPicker claims={searchResults} onSelectClaim={this.selectExistingClaim}/>
        }
      } else if (this.props.user) {
        return <ExistingClaimPicker claims={this.props.user.recentlyViewed} onSelectClaim={this.selectExistingClaim}/>
      }
    }
  }


  render(){
    const {userLoading, user} = this.props
    let submitClasses = `buttonUX2 addEvidenceFormButton ${this.props.evidenceType=="counter" ? "buttonUX2Red" : ""}`
    return <Form onSubmit={this.props.onSubmit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { ({submitForm, values: {title}}) => (
        <ClaimSearch
          query={title}
          render={({results, searching}) =>
                  <form onSubmit={submitForm} className="addEvidenceForm">
                      <TitleText id="title" className="addEvidenceFormTextField"
                                   placeholder='Make a claim, eg "Dogs can learn more tricks than cats."'
                                   onFocus={() => {this.setState({titleTextFocused: true})}}
                                   // use the setTimeout here to allow the mousedown event in existingclaimpicker to fire consistently
                                   // right now this fires before the onClick in ExistingClaimPIcker and hides that UI before the click event can be fired
                                   // TODO: check in with josh to see if we can come up with better "hide" conditions
                                   onBlur={() => {setTimeout(() => this.setState({titleTextFocused: false}), 100)}}
                          />
                          {this.existingClaimPicker(title, results, searching)}
                        <button type="submit" className={submitClasses}>Add</button>
                          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
                    </form>
                  }/>
      )}
    </Form>
  }
}

export default graphql(schema.CurrentUserQuery, {
  props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
    userLoading: loading,
    user: currentUser,
    refetchUser: refetch
  })
})(AddEvidenceForm)
