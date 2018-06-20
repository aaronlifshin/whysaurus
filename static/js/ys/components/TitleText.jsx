import React from 'react'
import { graphql } from 'react-apollo';
import { Form, Text, TextArea, Field } from 'react-form'
import PropTypes from 'prop-types'

import * as validations from '../validations'
import * as schema from '../schema';

import CharCount from './CharCount'
import ClaimSuggestor from './ClaimSuggestor'

// use onmousedown here to try to get in before blur hides the UI (see note in TitleText onBlur below)
// TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
// <li>example claim</li>
const ExistingClaimPicker = ({claims, onSelectClaim}) =>
  <div className="existingClaimPicker">
    <div className="existingClaimPickerHeading">You can also add an existing claim:</div>
    <ul className="existingClaimList">
          {claims && claims.map((claim) => <li onMouseDown={e => onSelectClaim(claim, e)} key={claim.id}>
                                {claim.title}
                                </li>)}

    </ul>
  </div>


class TitleText extends React.Component {
  static propTypes = {
    suggestExistingClaims: PropTypes.bool,
    point: PropTypes.object,
    evidenceType: PropTypes.string,
    addExistingClaim: PropTypes.func
  }

  constructor(props) {
    super(props)
    this.state = {titleTextFocused: false}
  }

  selectExistingClaim = (claim) =>
    this.props.addExistingClaim(this.props.evidenceType, claim)

  feedbackArea = (error, suggestions, searching) => {
    let errorClasses = `titleTextErrorArea ${error && "titleTextErrorAreaContent"}`
    let claimFeedbackAreaClasses = `claimFeedbackArea ${this.props.evidenceType=="counter" && "counter" }`
    return <div className={claimFeedbackAreaClasses}>
      <div className={errorClasses}>{error}</div>
      {suggestions && suggestions.length > 0 && <ExistingClaimPicker claims={suggestions} onSelectClaim={this.selectExistingClaim}/>}
    </div>
  }

  showFeedbackArea = (error, suggestions) =>
    this.state.titleTextFocused && (error || (this.props.suggestExistingClaims && suggestions && suggestions.length > 0 ))

  onEnterPress = (e) => {
    if(e.keyCode == 13) {
      e.preventDefault();
      this.props.onSubmit();
    }
  }

  // To make feedbackArea persistent change {titleTextFocused: false} to {titleTextFocused: true}
  renderCountedTextField = (title, textProps, error, suggestions, searching) =>
    <CharCount countedValue={title || ""} maxChars={validations.titleMaxCharacterCount} render={({charsLeft}) => (
      <span>
        <TextArea field="title" {...textProps} onKeyDown={this.onEnterPress}
              onFocus={() => {this.setState({titleTextFocused: true})}}
              // use the setTimeout here to allow the mousedown event in existingclaimpicker to fire consistently
              // right now this fires before the onClick in ExistingClaimPIcker and hides that UI before the click event can be fired
              // TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"

              // comment this out to make FeedbackArea persistant for styling
              onBlur={() => {setTimeout(() => this.setState({titleTextFocused: false}), 100)}}
          />
          <span className={"charCounter " + (charsLeft && charsLeft < 0 ? ' overMaxChars' : '')}>{charsLeft}</span>
          {this.showFeedbackArea(error, suggestions) && this.feedbackArea(error, suggestions, searching)}

      </span>
    )}/>


  // To make error area persistant change this line:
  //   const { value, error, warning, success, setValue, setTouched } = fieldApi
  // to:
  //   let { value, error, warning, success, setValue, setTouched } = fieldApi
  //   error = "THIS IS AN ERORR"
  render(){
    // `field` is here to strip out the field prop since we set it manually
    const { field, point, evidenceType, addExistingClaim, suggestExistingClaims, ...restOfProps } = this.props
    // add focused prop here to make Field.shouldComponentUpdate return true when focus changes
    return <Field field="title" focused={this.state.titleTextFocused}>
      {fieldApi => {
        const { value, error, warning, success, setValue, setTouched } = fieldApi
        let title = value
        return (
          <div className="claimTitleField">
            {this.props.suggestExistingClaims ? <ClaimSuggestor
                                                    query={title}
                                                    point={point}
                                                    evidenceType={evidenceType}
                                                    render={({suggestions, searching}) => this.renderCountedTextField(title, restOfProps, error, suggestions, searching)}/> :
              this.renderCountedTextField(title, restOfProps, error)}
          </div>
        )
      }}
    </Field>
  }
}

export default TitleText
