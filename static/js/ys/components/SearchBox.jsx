import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloProvider, graphql, compose, withApollo } from 'react-apollo';
import gql from 'graphql-tag';
import { ApolloClient } from 'apollo-client';

export class SearchBox extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      inputValue: '',
    };
  }

  componentDidMount() {
  }

  updateInputValue(val) {
    this.setState({
      inputValue: val
    });
  }

  // using public class fields syntax for this handler, to ensure proper binding of `this`
  getSearchResults = () => {
    console.log(`searchBox: getSearchResults (${this.state.inputValue})`);
  //   searchTerms = $("#searchBox").val();
  //   if (searchTerms == "") {
  //       return;
  //   }
  //   startSpinnerOnButton('.searchIcon');
    
  //   $.ajaxSetup({
  //     url: "/search",
  //     global: false,
  //     type: "POST",
  //     data: {
  //       'searchTerms': searchTerms,   
  //     },
  //     success: function(obj) {
  //       if (obj.result == 0) {
  //         showAlert("No results found for: <strong>" + obj.searchString + "</strong>");
  //       } else {
  //         $("#mainContainer").children().remove();
  //         $("#mainContainer").append(obj.html);
  //         makePointsCardsClickable();                 
  //       }
  //       stopSpinnerOnButton('.searchIcon', getSearchResults);                        
  //     },
  //     error: function(xhr, textStatus, error){
  //       showAlert('<strong>Oops!</strong> There was a problem during the search.  Refreshing and searching again might help.');            
  //         stopSpinnerOnButton('.searchIcon', getSearchResults);            
  //       }
  //   });
  //   $.ajax();
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
      </div>
    )
  }
}
