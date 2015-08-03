#!/bin/bash

suite='scraper.scraper_req_options_run_test.ScraperReqOptionsRunTest'
tests="
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done