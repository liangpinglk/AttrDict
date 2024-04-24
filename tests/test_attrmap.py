"""
Tests for the AttrMap class.
"""
import unittest

import nose2


class TestAttrMap(unittest.TestCase):
    def test_repr(self):
        """
        repr(AttrMap)
        """
        from attrdict.mapping import AttrMap

        self.assertEqual(repr(AttrMap()), "AttrMap({})")
        self.assertEqual(repr(AttrMap({'foo': 'bar'})), "AttrMap({'foo': 'bar'})")
        self.assertEqual(
            repr(AttrMap({1: {'foo': 'bar'}})), "AttrMap({1: {'foo': 'bar'}})"
        )
        self.assertEqual(
            repr(AttrMap({1: AttrMap({'foo': 'bar'})})),
            "AttrMap({1: AttrMap({'foo': 'bar'})})"
        )


if __name__ == '__main__':
    nose2.main()
