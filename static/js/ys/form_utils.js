export function withCharCount(WrappedComponent, maxChars) {
  return class extends React.Component {
    constructor(props) {
      super(props);
      this.updateCharCount = this.updateCharCount.bind(this);
      this.state = {
        charsLeft: props.countedValue ? (maxChars - props.countedValue.length) : maxChars
      };
    }

    updateCharCount(text) {
      this.setState({
        charsLeft: maxChars - text.length
      });
    }

    render() {
      // ... and renders the wrapped component with the fresh data!
      // Notice that we pass through any additional props
      return <WrappedComponent charsLeft={this.state.charsLeft} updateCharCount={this.updateCharCount} {...this.props} />;
    }
  };
}
