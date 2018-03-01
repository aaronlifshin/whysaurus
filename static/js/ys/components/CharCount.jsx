import React from 'react'
import PropTypes from 'prop-types'

export class CharCount extends React.Component {

  constructor(props) {
    super(props);
    this.updateCharCountOnChange = this.updateCharCountOnChange.bind(this);
    this.state = {
      charsLeft: props.countedValue ? (props.maxChars - props.countedValue.length) : props.maxChars
    };
  }

  updateCharCountOnChange(text) {
    this.setState({
      charsLeft: this.props.maxChars - text.length
    });
  }

  render(){
    return (
      this.props.render({charsLeft: this.state.charsLeft, countedFieldOnChange: this.updateCharCountOnChange})
    )
  }
}

CharCount.propTypes = {
  render: PropTypes.func.isRequired,
  maxChars: PropTypes.number.isRequired
}

export default CharCount
