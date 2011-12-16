from dynamic_scraper.utils.test_utils import build_test_suite_from
from scraper.scraper_run_test import ScraperRunTest
from scraper.checker_run_test import CheckerRunTest
from scraper.pagination_test import PaginationTest
from scraper.model_test import ModelTest

test_cases = [
    ScraperRunTest,
    CheckerRunTest,
    PaginationTest,
    ModelTest,
]

def suite():
    return build_test_suite_from(test_cases)
