from celery.task import task

from dynamic_scraper.utils.task_utils import TaskUtils

@task()
def run_checker_tests():
    t = TaskUtils()
    t.run_checker_tests()