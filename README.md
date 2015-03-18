whysaurus
=========

Whysaurus

License:

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

Basic Setup Instructions:

1. Clone
2. Get constants.py from a collaborator and put it in this directory
3. Get the [Google App Engine SDK/Launcher for Python](https://developers.google.com/appengine/downloads)
5. `bin/compilelessc.sh` -- for Windows try [WinLESS](http://www.winless.org), and only compile the files listed in bin/compilelessc.sh, and set their output (by right clicking on the files) to /static/css.
   For MAC we have used SimpLESS, but have needed to apply this patch: https://gist.github.com/hlop/4951717
6. `bin/run.sh` or run in the Google App Engine Launcher and set to port 8081

Detailed Setup Instructions:

1. Make a github account: https://github.com/

2. Get Directory:
Go to: https://github.com/aaronlifshin/whysaurus
Download the directory folder zip from the right column
Get constants.py from a collaborator and put it in the directory folder

3. Google App Engine:
Go to: https://cloud.google.com/appengine/downloads
Download and Install App Engine SDK for Python
Open GoogleAppEngineLauncher
File > Add existing application
Browse for directory folder
Admin port can be any number
Port needs to be 8081
Select row for your directory and click “run”
When you click “browse” you should be able to see the unstyled Whysaurus site in your Browser

4. SimpLESS:
Download and install SimpLESS: http://wearekiss.com/simpless
Open SimpLESS
In your directory folder, find less folder
From that folder drag and drop bootstrap.less, new.less and responsive.less into SimpLESS
For all three files, click on the fielder icon to change the path to static > css. Also change the responsive css file name to bootstrap-responsive.css
Click the refresh icons
You may need to apply this patch: https://gist.github.com/hlop/4951717/ (download gist, close SimpLESS, right-click SimpLESS in your applications folder and select show package contents, copy the downloaded less.js to SimpLESS\Resources\app\3p and overwrite the existing file
If you refresh your locally hosted Whysaurus page, it should now have the correct styling

5. Create a Whysaurus account

6. Make your Whysaurus account an admin
In GoogleAppEngineLauncher, click SDK Console
Select Datastore Viewer from the left menu
Select WhysaurusUser from the Entity Kind drop-down menu and click list entries
Click on the key of your new Whysaurus account
Change Admin to true
Scroll down to click save
Click Flush Memcache