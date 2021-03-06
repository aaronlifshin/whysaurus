import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { BrowserRouter, Switch, Route, Redirect, withRouter } from 'react-router-dom'
import { Provider as AlertProvider } from 'react-alert'

import {PointListWithPoint} from './ys/components/PointList';
import History from './ys/components/History';
import SearchResults from './ys/components/SearchResults';
import HomePage from './ys/components/HomePage';
import {ExpandedIndexProvider} from './ys/components/ExpandedIndex'
import QuickCreateClaim from './ys/components/QuickCreateClaim'

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

const alertOptions = {
  position: 'bottom center',
  timeout: 5000,
  transition: 'scale'
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
    return <div className="row pointPageContainer infiniteWidth">
      <div id="infiniteOrFiniteWidth" className="">
        <SearchResults q={params.get("q")}/>
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
      var pageUrl = '/search?q=' + searchTerms;
      this.props.history.push(pageUrl);

    }
    return <div></div>
  }
}

const SearchBox = withRouter(SearchBoxComponent)

class MakeArgumentComponent extends React.Component {
  // since the make argument button is currently not under react control, just create a
  // function that the classical JS can call into and make it globally available.
  //
  // once we convert the entire page to react this component should actually render the make argument button
  render(){
    window.makeArgument = () => {
      this.props.history.push(homeURL + "?focusQuickCreate=true");
      QuickCreateClaim.focus()
    }
    return <div></div>
  }
}

const MakeArgument = withRouter(MakeArgumentComponent)

const alertStyle = {
  backgroundColor: '#151515',
  color: 'white',
  padding: '10px',
  textTransform: 'uppercase',
  borderRadius: '3px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  boxShadow: '0px 2px 2px 2px rgba(0, 0, 0, 0.03)',
  fontFamily: 'Arial',
  // width: '300px',
  boxSizing: 'border-box'
}

const buttonStyle = {
  marginLeft: '20px',
  border: 'none',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  color: '#FFFFFF'
}

const AlertTemplate = ({ message, options, style, close }) => {
  return (
    <div style={{ ...alertStyle, ...style }}>
      <span style={{ flex: 2 }}>{message}</span>
      <button onClick={close} style={buttonStyle}>
        X
      </button>
    </div>
  )
}

class App extends React.Component {
  render() {
    return (<div>
        <MakeArgument/>
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
  <AlertProvider template={AlertTemplate} {...alertOptions}>
    <BrowserRouter>
      <ApolloProvider client={client}>
        <ExpandedIndexProvider>
          <App/>
        </ExpandedIndexProvider>
      </ApolloProvider>
    </BrowserRouter>
  </AlertProvider>,
  document.getElementById('root')
);
