import re
import unittest
from nose import tools
from nose.tools import *

__all__ = ['assert_instance_of', 'assert_not_instance_of',
           'assert_none', 'assert_not_none',
           'assert_list_same', 'assert_contains',
           'assert_match', 'assert_not_match'] + tools.__all__

def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args

def assert_instance_of(expected, actual, msg=None):
    """Verify that object is an instance of expected """
    assert isinstance(actual, expected), msg

def assert_not_instance_of(expected, actual, msg=None):
    """Verify that object is not an instance of expected """
    assert not isinstance(actual, expected, msg)

def assert_none(actual, msg=None):
    """verify that item is None"""
    assert_equal(None, actual, msg)

def assert_not_none(actual, msg=None):
    """verify that item is None"""
    assert_not_equal(None, actual, msg)

def assert_list_same(expected, actual, msg=None):
    """verify that the list contains the expected"""
    assert_equal([repr(e) for e in expected],
                 [repr(a) for a in actual])

def assert_contains(expected, actual, msg=None):
    """verify that the expected is in the actual"""
    assert_true(expected in actual, '%s was expected to be in %s, but was not found' % (expected, actual))

def assert_match(pattern, string, msg=None):
    """verify that the pattern matches the string"""
    assert_not_none(re.search(pattern, string), msg)

def assert_not_match(pattern, string, msg=None):
    """verify that the pattern does not match the string"""
    assert_none(re.search(pattern, string), msg)

