#!/bin/bash

suite='scraper.scraper_req_options_run_test.ScraperReqOptionsRunTest'
tests1="
test_with_request_type_post
test_with_custom_header
test_with_custom_body
test_with_form_data_simple
test_with_form_data_pagination
"

for (( i = 1; i <= 1; i++ ))
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