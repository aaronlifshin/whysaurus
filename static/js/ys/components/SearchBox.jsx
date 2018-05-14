import React from 'react'
import ReactDOM from 'react-dom'
import { ApolloProvider, graphql, compose, withApollo } from 'react-apollo'
import gql from 'graphql-tag'
import { ApolloClient } from 'apollo-client'
import { SearchResults } from './SearchResults'

export class SearchBox extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      inputValue: '',
      readyToSearch: false,
    };
  }

  componentDidMount() {
  }

  updateInputValue(val) {
    this.setState({
      inputValue: val,
    });
    if (val && val.length == 0) {
      this.setState({readyToSearch: false})
    }
  }

  // using public class fields syntax for this handler, to ensure proper binding of `this`
  getSearchResults = () => {
    console.log(`searchBox: getSearchResults (${this.state.inputValue})`)
    this.setState({readyToSearch: true})
    setTimeout(() => { this.setState({readyToSearch: false})}, 1000)
  }

  render() {
    // the searchIcon's click handler needs to be defined in an enclosing <span>, b/c the <svg> element 
    // that gets generated in span.searchIcon does not correctly receive an onClick function
    return (
      <div>
        <input id="searchBoxReact" type="text" name="searchTerms" placeholder="Find Argument..." results="0"
               onChange={(event) => this.updateInputValue(event.target.value)}
               onKeyUp={ (event) => {if (event.keyCode == 13) this.getSearchResults();} }
        />
        <span onClick={this.getSearchResults}>
          <span className="searchIcon pull-right fa fa-search"></span>
        </span>
        {this.state.readyToSearch && 
          <SearchResults searchValue={this.state.inputValue}/>
        }
      </div>
    )
  }
}
