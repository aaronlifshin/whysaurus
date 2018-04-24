import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloProvider, graphql, compose, withApollo } from 'react-apollo';
import gql from 'graphql-tag';
import { ApolloClient } from 'apollo-client';

export class SearchBox extends React.Component {
  constructor(props) {
    super(props)
  }

  getSearchResults() {
    console.log('searchBox: getSearchResults');
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

  componentDidMount() {
    const $this = $(ReactDOM.findDOMNode(this));
    setTimeout(() => {  //the "real" DOM isn't quite ready yet... window.requestAnimationFrame() didn't work, either
      $(".searchIcon", $this).click(event => this.getSearchResults());
    }, 500);
    console.log("searchBox: componentDidMount() - click event set up");
  }

  render() {
    return (
      <div>
        <input id="searchBoxReact" type="text" name="searchTerms" placeholder="Find Argument..." results="0"
               onKeyUp={ (event) => {if (event.keyCode == 13) this.getSearchResults(); } }
        />
        <span className="searchIcon pull-right fa fa-search"></span>
      </div>
    )
  }
}
