import React from 'react'
import * as validations from '../validations';
import * as formUtils from '../form_utils.js';
import { Form, Text, Field } from 'react-form';

const TitleFieldComponent = props => (
  <Field field={props.field}>
    {fieldApi => {
      const { updateCharCount, charsLeft, onChange, field, ...rest } = props

      const { value, error, warning, success, setValue, setTouched } = fieldApi

      return (
        <div className="titleField">
          <Text onChange={updateCharCount} field="title" {...rest}/>
          <p classes={charsLeft && charsLeft < 0 ? 'overMaxChars' : ''}>{charsLeft}</p>
          <p>{error}</p>
        </div>
      )
    }}
  </Field>
);
export const TitleText = formUtils.withCharCount(TitleFieldComponent, validations.titleMaxCharacterCount)
