#!/bin/bash
# gem install less
lessc less/bootstrap.less > static/css/bootstrap.css
lessc less/responsive.less > static/css/bootstrap-responsive.css
lessc less/new.less > static/css/new.css
lessc less/uiv2.less > static/css/uiv2.css
