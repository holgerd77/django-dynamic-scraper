from dynamic_scraper.utils.test_utils import build_test_suite_from
from basic.processors_test import ProcessorsTest
from basic.scheduler_test import SchedulerTest

test_cases = [
    ProcessorsTest,
    SchedulerTest,
]

def suite():
    return build_test_suite_from(test_cases)