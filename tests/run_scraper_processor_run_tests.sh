#!/bin/bash

suite='scraper.scraper_processor_run_test.ScraperProcessorRunTest'
tests1="
test_processor
test_multiple_processors_use
test_replace_processor_wrong_x_path
test_replace_processor_correct_x_path
test_replace_processor_unicode_replace
test_static_processor_wrong_x_path
"
tests2="
test_static_processor_empty_x_path
test_static_processor_correct_x_path
test_static_processor_unicode_text
test_reg_exp
test_processor_with_detail_page_url_placeholder
test_processor_with_placeholder_mp_to_dp
"
tests3="
test_processor_with_placeholder_mp_to_dp_unicode
test_processor_with_placeholder_dp_to_mp
test_processor_with_placeholder_tmp_to_mp
test_processor_with_placeholder_tmp_with_placeholder_to_mp
"

for (( i = 1; i <= 3; i++ ))
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