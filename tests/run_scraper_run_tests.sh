#!/bin/bash

suite='scraper.scraper_run_test.ScraperRunTest'
tests="
test_missing_url_elem
test_scraper
test_double
test_detail_page_url_id_field
test_single_standard_id_field
test_double_standard_id_field
test_standard_update_field
test_standard_update_field_update
test_save_to_db
test_save_to_db_non_model_attribute
test_testmode
test_task_run_type
test_no_task_run_type
test_runtime_config_max_items_read
test_runtime_config_max_items_save
test_max_items_read
test_max_items_save
test_missing_mandatory
test_scraper_pause_status
test_scraper_inactive_status
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done