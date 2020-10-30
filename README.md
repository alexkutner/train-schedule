# train-schedule

dependencies
pipenv

## To run
- clone repo
- pipenv install
- pipenv shell
- export FLASK_APP=flaskr
- export FLASK_ENV=development  # to enable debugger
- flask run

## Run test
- pytest

## Code
- handlers for web requests lives in flaskr/routes.py
- db logic wrapping rocksdb lives in flaskr/db.py
- logic to build up a set of concurrent trains and search that set lives in flaskr/concurrent_trains.py
- tests live in tests

## Assumptions:
- We want to return accurate results for every query
- That there will be multiple instances of this service running


## Results:
- We are building the concurrent data structure for each request as we can't build it when data is added because we 
don't have a way to deal with two updates coming in on two servers at the same time.  Ideally this work db io and 
searching for matches would be done when the service starts up or when the db state is mutated.  Making this change would 
not be to hard as the data structure should just be added to the server context.

## Known issues
- Have not yet added application logging
- missing swagger API docs