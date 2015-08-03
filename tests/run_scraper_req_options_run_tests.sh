#!/bin/bash

suite='scraper.scraper_req_options_run_test.ScraperReqOptionsRunTest'
tests="
test_with_form_data_simple
test_with_form_data_pagination
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done