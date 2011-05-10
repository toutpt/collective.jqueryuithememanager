import doctest
import unittest2 as unittest

from Testing import ZopeTestCase as ztc
import base


def test_suite():

    TEST_CLASS = base.FunctionalTestCase
    OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'theme.txt',package='collective.jqueryuithememanager.tests',
            test_class=TEST_CLASS,
            optionflags=OPTIONFLAGS
            ),

        ])