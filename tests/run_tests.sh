#!/bin/bash

./run_basic_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_scraper_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_scraper_processor_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_scraper_req_options_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_scraper_img_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_scraper_json_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_checker_run_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_pagination_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi
./run_model_tests.sh
if [ "$?" -gt 0 ]
then
    exit 1
fi

