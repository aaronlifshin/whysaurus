whysaurus
=========

Whysaurus

License:

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

Basic Setup Instructions:

1. Clone
2. Get `constants.py` from a collaborator and put it in the root directory of this project (the directory this file lives in)
3. Follow steps 1-5 on https://cloud.google.com/appengine/docs/standard/python/download
4. Install `less`
- OSX: `brew install npm && npm install -g less`
- OSX Alternative: SimpLESS, but have needed to apply this patch: https://gist.github.com/hlop/4951717
- Windows: try [WinLESS](http://www.winless.org), and only compile the files listed in bin/compilelessc.sh, and set their output (by right clicking on the files) to /static/css.
5. Run `bin/compilelessc.sh` to compile CSS resources
   For Linux just run `npm install -g less`
6. Set the data storage location for local development
7. `bin/run.sh` or run in the Google App Engine Launcher and set to port 8081

Detailed Setup Instructions:

1. Make a github account: https://github.com/

2. Get Directory:<br />
* Go to: https://github.com/aaronlifshin/whysaurus
* Download the directory folder zip from the right column
* Get constants.py from a collaborator and put it in the directory folder

3. Google App Engine:
* Go to: https://cloud.google.com/appengine/docs/standard/python/download
* Follow steps 1 - 5 to install python 27, the app sdk, and the components for DJango

4. Install Less
* OSX Homebrew
  * Install (Homebrew)[https://brew.sh/]
  * Install npm: `brew install npm`
  * Install less: `npm install -g less`
* SimpLESS:
  * Download and install SimpLESS: http://wearekiss.com/simpless
  * Open SimpLESS
  * In your directory folder, find less folder
  * From that folder drag and drop bootstrap.less, new.less and responsive.less into SimpLESS
  * For all three files, click on the fielder icon to change the path to static > css. Also change the responsive css file name to bootstrap-responsive.css
  * Click the refresh icons
  * You may need to apply this patch: https://gist.github.com/hlop/4951717/ (download gist, close SimpLESS, right-click SimpLESS in your applications folder and select show package contents, copy the downloaded less.js to SimpLESS\Resources\app\3p and overwrite the existing file
  * If you refresh your locally hosted Whysaurus page, it should now have the correct styling

5. Create a Whysaurus account using email (google and facebook don't work locally, currently)

6. Make your local Whysaurus account an admin
(Currently a different procedure than making a user admin on staging or production!)
* Go to the local console at http://localhost:8000/console
* Select WhysaurusUser from the Entity Kind drop-down menu and click list entries
* Click on the key of your new Whysaurus account
* Change Admin to true
* Scroll down to click save
* Click Flush Memcache

7. Data storage for local development environment
* If you'd like to prevent your local database and search indexes from being truncated every few days, add the following option to the dev_appserver.py command in bin/run.sh:
  * --storage_path=~/<directory_in_your_user_tree>
* If at some point you need to clear your local database and/or search indexes, start dev_appserver.py with one or both of these options:
  * --clear_datastore True
  * --clear_search_indexes True
