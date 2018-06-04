import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { BrowserRouter, Switch, Route, Redirect, withRouter } from 'react-router-dom'

import {PointListWithPoint} from './ys/components/PointList';
import History from './ys/components/History';
import SearchResults from './ys/components/SearchResults';
import {HomePage} from './ys/home';
import {ExpandedIndexProvider} from './ys/components/ExpandedIndex'

const client = new ApolloClient({
  link: new HttpLink({ uri: '/graphql', credentials: 'same-origin' }),
  cache: new InMemoryCache()
});

const homeURL = "/"

class PointPage extends React.Component {

  state = {goHome: false}

  render(){
    if (this.state.goHome){
      return <Redirect to={homeURL}/>
    } else {
      return <div className="row pointPageContainer infiniteWidth">
        <div id="infiniteOrFiniteWidth" className="">
          <PointListWithPoint url={this.props.match.params.url} onDelete={() => {this.setState({goHome: true})}}/>
        </div>
      </div>
    }
  }
}

class HistoryPage extends React.Component {

  render(){
      return <div className="row pointPageContainer infiniteWidth">
        <div id="content" className="fullPageText">
          <History url={this.props.match.params.url}/>
        </div>
      </div>
  }
}


class SearchPage extends React.Component {
  render(){
    const params = new URLSearchParams(this.props.location.search)
    this.props.history.listen((location, action) => {
      console.log(
        `The current URL is ${location.pathname}${location.search}${location.hash}`
      )
      console.log(`The last navigation action was ${action}`)
    })
    console.log("rerendering searhc")
    return <div className="row pointPageContainer infiniteWidth">
      <div id="infiniteOrFiniteWidth" className="">
        <SearchResults query={params.get("query")}/>
      </div>
    </div>
  }
}

class SearchBoxComponent extends React.Component {
  // since the search box is currently not under react control, just create a
  // function that the classical JS can call into and make it globally available.
  //
  // once we convert the entire page to react this component should actually render the search box.
  render(){
    window.onSearch = (searchTerms) => {
      var pageUrl = '/search?query=' + searchTerms;
      this.props.history.push(pageUrl);

    }
    return <div></div>
  }
}

const SearchBox = withRouter(SearchBoxComponent)

class App extends React.Component {
  render() {
    return (<div>
        <SearchBox/>
        <Switch>
        <Route exact path={homeURL} component={HomePage} />
        <Route exact path="/claim/:url" component={PointPage} />
        <Route exact path="/history/:url" component={HistoryPage} />
        <Route exact path="/search" component={SearchPage} />
            </Switch>
            </div>
    )
  }
}

ReactDOM.render(
  <BrowserRouter>
    <ApolloProvider client={client}>
      <ExpandedIndexProvider>
        <App/>
      </ExpandedIndexProvider>
    </ApolloProvider>
  </BrowserRouter>,
  document.getElementById('root')
);
