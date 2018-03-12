import React from 'react'
import PropTypes from 'prop-types'
import { Form, Text, Field } from 'react-form'
import CharCount from './CharCount'
import * as validations from '../validations'

const TitleText = props => (
  <Field field={props.field}>
    {fieldApi => {
      // field is here to strip that property out of `rest`
      const { field, ...rest } = props
      const { value, error, warning, success, setValue, setTouched } = fieldApi

      return (
        <div className="titleField">
          <CharCount countedValue={value.title} maxChars={validations.titleMaxCharacterCount} render={({charsLeft}) => (
            <div>
              <Text field="title" {...rest}/>
              <p classes={charsLeft && charsLeft < 0 ? 'overMaxChars' : ''}>{charsLeft}</p>
              <p>{error && error.title}</p>
            </div>
              )}/>
        </div>
      )
    }}
  </Field>
);

TitleText.propTypes = {
}

export default TitleText
