# coding=utf-8
"""
Tests for Zipfs Law analysis
"""
import unittest

import parse_epub


class ZipfsLawTests(unittest.TestCase):
    """
    Tests for Zipfs Law analysis
    """

    def test_zipfs_law_hitchhiker(self):
        """
        Test using Hitchhiker Guide
        """
        parse_epub.zipfs_law_analysis('hitchhiker.epub')


if __name__ == '__main__':
    unittest.main()
