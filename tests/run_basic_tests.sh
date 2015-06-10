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