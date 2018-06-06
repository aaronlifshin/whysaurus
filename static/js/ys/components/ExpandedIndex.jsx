import React from 'react'
import { withRouter } from 'react-router';

const Context = React.createContext(
  {index: {},
   expand: () => {},
   collapse: () => {},
   isExpanded: () => {}
  }
);

class ExpandedIndexProviderComponent extends React.Component {

  constructor(props) {
    super(props);

    // create state this way because we need a consistent object identity to
    // pass to the provider value - see the caveats here:
    // https://reactjs.org/docs/context.html
    this.state = {
      index: this.urlExpandedIndex(),
      expand: this.expand,
      collapse: this.collapse,
      isExpanded: this.isExpanded
    }
  }

  expandedIndex2Param = (index) => {
    return Object.keys(index).filter(key => index[key]).toString()
  }

  expandedParam2Index = (param) => {
    try {
      return param ? param.split(",").reduce((i, k) => {i[k] = true; return i}, {}) : {}
    } catch (err) {
      console.log("Error parsing URL expanded index:")
      console.log(param)
      console.log(err)
      return {}
    }
  }

  urlExpandedIndex = (urlSearchParams) => {
    let params = urlSearchParams || new URLSearchParams(this.props.location.search)
    return this.expandedParam2Index(params.get("expanded"))
  }

  updateURLExpandedIndex = (urlSearchParams, updatedIndex) => {
    let params = urlSearchParams || new URLSearchParams(this.props.location.search)
    if (Object.entries(updatedIndex).length > 0) {
      params.set("expanded", this.expandedIndex2Param(updatedIndex))
    } else {
      params.delete("expanded")
    }
    const { location, history } = this.props
    history.push({path: location.pathname, search: params.toString()})
  }

  modifyStateAndURL = (point, indexModifier) => {
    let params = new URLSearchParams(this.props.location.search);
    let index = this.urlExpandedIndex()
    indexModifier(index)
    this.setState({index: index})
    this.updateURLExpandedIndex(params, index)
  }

  expansionIndexKey = (point, prefix) => (prefix || "") + point.url

  expand = (point, prefix) => {
    this.modifyStateAndURL(point, index => index[this.expansionIndexKey(point, prefix)] = true)
  }

  collapse = (point, prefix) => {
    this.modifyStateAndURL(point, index => delete index[this.expansionIndexKey(point, prefix)])
  }

  isExpanded = (point, prefix) => !!this.state.index[this.expansionIndexKey(point, prefix)]

  render(){
    // IMPORTANT: value must always point at state so that the context has a consistent reference
    // see the "caveats" section of https://reactjs.org/docs/context.html for more information
    return <Context.Provider value={this.state}>
        {this.props.children}
      </Context.Provider>
  }
}

export const ExpandedIndexProvider =  withRouter(ExpandedIndexProviderComponent);


export function withExpandedIndexForPoint(Component) {
  return function ExpandedIndexComponent(props){
    const {point, prefix} = props
    return (
      <Context.Consumer>
        {expansion => <Component {...props}
                                 expanded={expansion.isExpanded(point, prefix)}
                                 onExpand={() => expansion.expand(point, prefix)}
                                 onCollapse={() => expansion.collapse(point, prefix)}
                                 expansion={expansion} />}
      </Context.Consumer>
    )
  }
}

export function withExpandedIndex(Component) {
  return function ExpandedIndexComponent(props){
    return (
      <Context.Consumer>
        {expansion => <Component {...props} expansion={expansion} />}
      </Context.Consumer>
    )
  }
}
