#!/bin/bash

suite='scraper.scraper_js_run_test.ScraperJSRunTest'
tests="
test_default_no_scrapyjs_main_page
test_default_no_scrapyjs_detail_page
test_activated_scrapyjs_main_page
test_activated_scrapyjs_detail_page
test_default_no_scrapyjs_checker_delete
test_default_no_scrapyjs_checker_no_delete
test_activated_scrapyjs_checker_delete
test_activated_scrapyjs_checker_no_delete
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done
