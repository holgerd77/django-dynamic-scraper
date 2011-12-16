#!/bin/bash

app='basic'
tests="
ProcessorsTest 
SchedulerTest
"

for test in `echo $tests`
do
	python manage.py test $app.$test
done

app='scraper'
tests="
ScraperRunTest.test_missing_base_elem
ScraperRunTest.test_missing_url_elem
ScraperRunTest.test_scraper
ScraperRunTest.test_testmode
ScraperRunTest.test_num_items
ScraperRunTest.test_missing_mandatory
ScraperRunTest.test_processor
ScraperRunTest.test_reg_exp
ScraperRunTest.test_with_imgs
CheckerRunTest.test_keep_video
CheckerRunTest.test_404_delete
CheckerRunTest.test_404_delete_with_img
CheckerRunTest.test_x_path_delete
PaginationTest.test_config_append_str_without_page
PaginationTest.test_config_wrong_range_format
PaginationTest.test_p_on_start
PaginationTest.test_one_page
ModelTest.test_scraper_get_scrape_elems
ModelTest.test_scraper_get_mandatory_scrape_elems
"

for test in `echo $tests`
do
	python manage.py test $app.$test
done

