# train-schedule

dependencies
pipenv

##to run
-clone repo
-pipenv install
-pipenv shell
-export FLASK_APP=flaskr
-export FLASK_ENV=development  # to enable debugger
-flask run

##run test
-pytest

assumptions:
-We want to return accurate results for every query
-That there will be multiple instances of this service running


results:
We are building the concurrent data structure for each request as we can't build it when data is added because we don't have a way to deal with two updates coming in on two servers at the same time.