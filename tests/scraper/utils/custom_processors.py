from __future__ import unicode_literals
from builtins import str


def custom_post_string(text, loader_context):
    post_str = loader_context.get('custom_post_string', '')
    
    return text + "_test_" + post_str