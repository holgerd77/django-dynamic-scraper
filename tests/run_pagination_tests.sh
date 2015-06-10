#!/bin/bash


suite='scraper.pagination_test.PaginationTest'
tests="
test_config_append_str_without_page
test_p_on_start
test_range_funct_type_wrong_replace_format
test_range_funct_type_one_page
test_free_list_type_wrong_replace_format
test_free_list_type_scraper_run
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done