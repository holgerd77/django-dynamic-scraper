#!/bin/bash


suite='scraper.scraper_json_run_test.ScraperJSONRunTest'
tests="
test_num_scraped_objects
test_non_repetition
test_non_data_mixing
test_detail_page
test_detail_page_json
test_checker_x_path_type_x_path_delete
test_checker_x_path_type_x_path_no_delete
test_json_checker_x_path_type_x_path_delete
test_json_checker_x_path_type_x_path_no_delete
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done