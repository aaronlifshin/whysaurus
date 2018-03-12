import React from 'react'
import PropTypes from 'prop-types'

export default class CharCount extends React.Component {
  static propTypes = {
    render: PropTypes.func.isRequired,
    countedValue: PropTypes.number.isRequired,
    maxChars: PropTypes.number.isRequired
  }

  render(){
    const {render, countedValue, maxChars} = this.props
    return (
      this.props.render({charsLeft: (countedValue ? (maxChars - countedValue.length) : maxChars)})
    )
  }
}
