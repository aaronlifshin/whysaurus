import React from 'react';
import ReactDOM from 'react-dom';
import {PostListWithPoints, PointListWithPoints, PointListWithPoint} from './ys/point_list';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';

const client = new ApolloClient({
  link: new HttpLink({ uri: '/graphql', credentials: 'same-origin' }),
  cache: new InMemoryCache()
});

let templateData = document.getElementById('config').dataset
ReactDOM.render(
  <ApolloProvider client={client}><PointListWithPoint/></ApolloProvider>,
  document.getElementById('root')
);
