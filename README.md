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

2. Get Directory:<br />
Go to: https://github.com/aaronlifshin/whysaurus<br />
Download the directory folder zip from the right column<br />
Get constants.py from a collaborator and put it in the directory folder<br />

3. Google App Engine:<br />
Go to: https://cloud.google.com/appengine/downloads<br />
Download and Install App Engine SDK for Python<br />
Open GoogleAppEngineLauncher<br />
File > Add existing application<br />
Browse for directory folder<br />
Admin port can be any number<br />
Port needs to be 8081<br />
Select row for your directory and click “run”<br />
When you click “browse” you should be able to see the unstyled Whysaurus site in your Browser<br />

4. SimpLESS:<br />
Download and install SimpLESS: http://wearekiss.com/simpless<br />
Open SimpLESS<br />
In your directory folder, find less folder<br />
From that folder drag and drop bootstrap.less, new.less and responsive.less into SimpLESS<br />
For all three files, click on the fielder icon to change the path to static > css. Also change the responsive css file name to bootstrap-responsive.css<br />
Click the refresh icons<br />
You may need to apply this patch: https://gist.github.com/hlop/4951717/ (download gist, close SimpLESS, right-click SimpLESS in your applications folder and select show package contents, copy the downloaded less.js to SimpLESS\Resources\app\3p and overwrite the existing file<br />
If you refresh your locally hosted Whysaurus page, it should now have the correct styling<br />

5. Create a Whysaurus account

6. Make your Whysaurus account an admin<br />
In GoogleAppEngineLauncher, click SDK Console<br />
Select Datastore Viewer from the left menu<br />
Select WhysaurusUser from the Entity Kind drop-down menu and click list entries<br />
Click on the key of your new Whysaurus account<br />
Change Admin to true<br />
Scroll down to click save<br />
Click Flush Memcache<br />
