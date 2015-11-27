#Stage 2 Update (Python 3)
from builtins import map
import unittest

def build_test_suite_from(test_cases):
    """
    Returns a single or group of unittest test suite(s) that's ready to be
    run. The function expects a list of classes that are subclasses of
    TestCase.

    The function will search the module where each class resides and
    build a test suite from that class and all subclasses of it.
    """
    test_suites = []
    for test_case in test_cases:
        mod = __import__(test_case.__module__)
        components = test_case.__module__.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        tests = []
        for item in list(mod.__dict__.values()):
            if type(item) is type and issubclass(item, test_case):
                tests.append(item)
        test_suites.append(unittest.TestSuite(list(map(unittest.TestLoader().loadTestsFromTestCase, tests))))
    return unittest.TestSuite(test_suites)