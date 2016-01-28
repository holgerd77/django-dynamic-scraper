#!/bin/bash


suite='scraper.scraper_json_run_test.ScraperJSONRunTest'
tests1="
test_num_scraped_objects
test_non_repetition
test_non_data_mixing
test_static_processor_empty_x_path
test_detail_page
test_detail_page_json
"
tests2="
test_checker_x_path_type_x_path_delete
test_checker_x_path_type_x_path_no_delete
test_json_checker_x_path_type_x_path_delete
test_json_checker_x_path_type_x_path_no_delete
"

for (( i = 1; i <= 2; i++ ))
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