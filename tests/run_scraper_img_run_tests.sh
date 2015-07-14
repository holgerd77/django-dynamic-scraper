#!/bin/bash

suite='scraper.scraper_img_run_test.ScraperImgRunTest'
tests="
test_img_store_format_flat_no_thumbs
test_img_store_format_flat_with_thumbs
test_img_store_format_all_no_thumbs
test_img_store_format_all_with_thumbs
test_img_store_format_thumbs_with_thumbs
test_missing_img_when_img_field_not_mandatory
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done