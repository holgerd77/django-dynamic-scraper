#!/bin/bash


suite='scraper.checker_run_test.CheckerRunTest'
tests1="
test_no_checker
test_x_path_type_keep
test_x_path_type_keep_double
test_x_path_type_blank_result_field_keep
test_x_path_type_404_delete
test_x_path_type_404_delete_with_zero_actions
"
tests2="
test_x_path_type_x_path_delete
test_x_path_type_x_path_first_delete_double
test_x_path_type_x_path_second_delete_double
test_x_path_type_blank_result_field_x_path_delete
test_delete_with_img_flat_no_thumbs
test_delete_with_img_flat_with_thumbs
"
tests3="
test_delete_with_img_all_no_thumbs
test_delete_with_img_all_with_thumbs
test_delete_with_img_thumbs_with_thumbs
test_404_type_404_delete
test_checker_test_wrong_checker_config
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