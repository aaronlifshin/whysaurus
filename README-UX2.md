# UX 2.0 README

This is a work in progress. Let's keep notes for 2.0 here and integrate 
into the regular docs as we progress.

The prototype uses https://facebook.github.io/react/ to build a fast, clean, recursive point interaction. React relies on webpack to compile JSX to JavaScript, so we add it to the build and development process here. We should be using a tool like webpack to bundle our scripts and stylesheets anyway, so this is an improvement on its own. Pragmatically, this should mean an extra `npm run webpack-watch` during development and `npm run bundle` before deployment.

# Installation

1. Follow the normal Whysaurus installation instructions. You may want to use the instructions here https://github.com/aaronlifshin/whysaurus/pull/17/files until that PR gets merged to master
2. Make sure you have `npm` installed. If you use `homebrew` on a Mac, you can do `brew install npm`. If you're on another platform, see the instructions here to get started: https://docs.npmjs.com/getting-started/installing-node
*Windows 10 seems to work fine, but we haven't gotten this to work on Windows 7 yet (have tried multiple approaches, including via cygwin).
3. In your project directory, run `npm install`. On windows, be sure to run as admin.
4. On windows run `npm install webpack -g`
5. Run `npm run bundle`

Every time package.json is updated
1. Re-run npm install
2. Re-run npm run bundle

# Running

1. Run Whysaurus as usual (we recommend `bin/run.sh`)
2. Navigate to a point, and replace `point` with `pointCard` in the URL. For example, if your point is at http://localhost:8081/point/HAm_is_gr8, modify the URL to http://localhost:8081/pointCard/HAm_is_gr8 and hit enter.

# Developing

1. While developing, you should use `npm run webpack-watch` to run webpack automatically when source code changes.
2. It may be useful to use `curl` to test changes to `schema.py`, for example like:

```
curl -v localhost:8081/graphql -d '{ point(url: "birds_are_fine") { title, upVotes }}'
```

or

```
curl localhost:8081/graphql -d 'mutation Vote {
  vote(url: "fish_are_ok", vote: -1) {
    point {
      title
      upVotes
      downVotes
    }
  }
}
'
```

# Code organization

The code for the V2 UX lives in two places.

The backend logic, implemented using [Graphene GAE](https://github.com/graphql-python/graphene-gae), a derivative of the [Graphene](https://github.com/graphql-python/graphene) GraphQL schema library, lives in [schema.py](./schema.py).

The frontend logic, implemented using [React](https://reactjs.org/), a UI framework and [Apollo](https://www.apollographql.com/), a JavaScript GraphQL framework, starts in [static/js/app.js](./static/js/app.js), which loads files in the [static/js/ys](./static/js/ys) directory. Most new functionality will be added to [static/js/ys/point.js](./static/js/ys/point.js).

New functionality will typically require a developer to A) add logic to `schema.py` to get or mutate data from the database, returning a result using standard GraphQL/Graphene techniques and B) add logic to `static/js/ys/point.js` to implement new UI or new UX affordances for manipulating data. https://github.com/aaronlifshin/whysaurus/commit/a69c57be66c44ff8f175a2762368e995becbe379 is a good example of a change that adds new data to the UI. https://github.com/aaronlifshin/whysaurus/commit/d676774662dbd163999ce55e80b68b7f8fc5d8a7 is a good example of a change that adds new data mutate capabilities (ie, title editing).

# FAQ

**Q:** I made changes in app.js that aren't showing up in the browser
**A:** Verify webpack is running - if there isn't already a terminal running `npm run webpack-watch` in the root directory of this project, go run that.

**Q:** I made changes in the CSS that aren't showing up in the browser
**A:** Go run `bin/compilelessc.sh` *[ed: I don't think we have a standard way of running this in an auto-compile way, but webpack might already be able to compile LESS so we should investigate that and eliminate this problem entirely]*
-- fwiw I am running WinLess, which auto-compiles less to css everytime it detects a change to a specified less file. I believe there is a mac equivalent. -JF
