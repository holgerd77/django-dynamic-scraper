#!/bin/bash

suite='scraper.scraper_js_run_test.ScraperJSRunTest'
tests1="
test_default_no_scrapyjs_main_page
test_default_no_scrapyjs_detail_page
test_activated_scrapyjs_main_page
test_activated_scrapyjs_detail_page
test_only_main_page_scrapyjs_main_page
test_default_no_scrapyjs_checker_delete
"
tests2="
test_default_no_scrapyjs_checker_no_delete
test_activated_scrapyjs_checker_delete
test_activated_scrapyjs_checker_no_delete
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
