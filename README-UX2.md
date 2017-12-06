# UX 2.0 README

This is a work in progress. Let's keep notes for 2.0 here and integrate 
into the regular docs as we progress.

The prototype uses https://facebook.github.io/react/ to build a fast, clean, recursive point interaction. React relies on webpack to compile JSX to JavaScript, so we add it to the build and development process here. We should be using a tool like webpack to bundle our scripts and stylesheets anyway, so this is an improvement on its own. Pragmatically, this should mean an extra `npm run webpack-watch` during development and `npm run bundle` before deployment.

# Installation

1. Follow the normal Whysaurus installation instructions. You may want to use the instructions here https://github.com/aaronlifshin/whysaurus/pull/17/files until that PR gets merged to master
2. Make sure you have `npm` installed. If you use `homebrew` on a Mac, you can do `brew install npm`. If you're on another platform, see the instructions here to get started: https://docs.npmjs.com/getting-started/installing-node
Windows 7 gave us trouble but Windows 10 seems to work fine.
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

# FAQ

**Q:** I made changes in app.js that aren't showing up in the browser
**A:** Verify webpack is running - if there isn't already a terminal running `npm run webpack-watch` in the root directory of this project, go run that.

**Q:** I made changes in the CSS that aren't showing up in the browser
**A:** Go run `bin/compilelessc.sh` *[ed: I don't think we have a standard way of running this in an auto-compile way, but webpack might already be able to compile LESS so we should investigate that and eliminate this problem entirely]*
-- fwiw I am running WinLess, which auto-compiles less to css everytime it detects a change to a specified less file. I believe there is a mac equivalent. -JF
