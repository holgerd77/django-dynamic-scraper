#!/bin/bash

app='basic'
tests="
processors_test.ProcessorsTest 
scheduler_test.SchedulerTest
"

for test in `echo $tests`
do
	echo $app.$test
    python manage.py test $app.$test
done

suite='scraper.scraper_run_test.ScraperRunTest'
tests="
test_missing_base_elem
test_missing_url_elem
test_scraper
test_standard_field_as_detail_page_url_hack
test_double
test_standard_update_field
test_standard_update_field_update
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
test_processor
test_multiple_processors_use
test_replace_processor_wrong_x_path
test_replace_processor_correct_x_path
test_static_processor_wrong_x_path
test_static_processor_correct_x_path
test_reg_exp
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

suite='scraper.scraper_json_run_test.ScraperJSONRunTest'
tests="
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done

suite='scraper.checker_run_test.CheckerRunTest'
tests="
test_checker_test_wrong_checker_config
test_none_type
test_x_path_type_keep_video
test_x_path_type_blank_result_field_keep_video
test_x_path_type_404_delete
test_x_path_type_404_delete_with_zero_actions
test_x_path_type_x_path_delete
test_x_path_type_blank_result_field_x_path_delete
test_delete_with_img_flat_no_thumbs
test_delete_with_img_flat_with_thumbs
test_delete_with_img_all_no_thumbs
test_delete_with_img_all_with_thumbs
test_delete_with_img_thumbs_with_thumbs
test_404_type_404_delete
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done

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

suite='scraper.model_test.ModelTest'
tests="
test_scraper_get_scrape_elems
test_scraper_get_mandatory_scrape_elems
"

for test in `echo $tests`
do
    echo $suite.$test
    python manage.py test $suite.$test
done

