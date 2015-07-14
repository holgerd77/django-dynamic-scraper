#!/bin/bash

suite='scraper.scraper_processor_run_test.ScraperProcessorRunTest'
tests="
test_processor
test_multiple_processors_use
test_replace_processor_wrong_x_path
test_replace_processor_correct_x_path
test_static_processor_wrong_x_path
test_static_processor_correct_x_path
test_reg_exp
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done