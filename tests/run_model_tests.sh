#!/bin/bash


suite='scraper.model_test.ModelTest'
tests="
test_scraper_get_scrape_elems
test_scraper_get_mandatory_scrape_elems
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done