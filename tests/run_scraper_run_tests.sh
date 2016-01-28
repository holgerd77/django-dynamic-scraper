#!/bin/bash

suite='scraper.scraper_run_test.ScraperRunTest'
tests1="
test_missing_url_elem
test_scraper
test_double
test_detail_page_url_id_field
test_single_standard_id_field
test_double_standard_id_field
"
tests2="
test_standard_update_field
test_standard_update_field_update
test_save_to_db
test_save_to_db_non_model_attribute
test_testmode
test_task_run_type
"
tests3="
test_no_task_run_type
test_runtime_config_max_items_read
test_runtime_config_max_items_save
test_max_items_read
test_max_items_save
test_missing_mandatory
"
tests4="
test_unicode_standard_field_main_page
test_unicode_standard_field_detail_page
test_scraper_pause_status
test_scraper_inactive_status
"

for (( i = 1; i <= 4; i++ ))
do
  var="tests$i"
  for test in `echo ${!var}`
  do
      echo $suite.$test
      python manage.py test $suite.$test &
      sleep 0.2
  done
  wait
done

