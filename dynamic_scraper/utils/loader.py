#Stage 2 Update (Python 3)
import logging, sys

from jsonpath_rw import jsonpath, parse

from scrapy.loader import ItemLoader
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.python import flatten


class JsonItemLoader(ItemLoader):

    def _get_xpathvalues(self, xpaths, **kw):
        self._check_selector_method()
        jsonpath_expr = parse(xpaths)
        res_list = [match.value for match in jsonpath_expr.find(self.selector)]
        return flatten(res_list)