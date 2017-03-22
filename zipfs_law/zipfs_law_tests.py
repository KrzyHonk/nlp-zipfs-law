# coding=utf-8
"""
Tests for Zipfs Law analysis
"""
import logging
import sys
import unittest

from zipfs_law import zipfs_law_analysis


class ZipfsLawTests(unittest.TestCase):
    """
    Tests for Zipfs Law analysis
    """

    def test_zipfs_law_hitchhiker(self):
        """
        Test using Hitchhiker Guide
        """
        zipfs_law_analysis.zipfs_law_analysis('hitchhiker')

        log = logging.getLogger("ZipfsLawTests.test_zipfs_law_hitchhiker")


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("SomeTest.testSomething").setLevel(logging.DEBUG)
    unittest.main()
