"""
Tests for the AttrDefault class.
"""
import unittest

import nose2
from six import PY2


class TestAttrDefault(unittest.TestCase):
    def test_method_missing(self):
        """
        default values for AttrDefault
        """
        from attrdict.default import AttrDefault

        default_none = AttrDefault()
        default_list = AttrDefault(list, sequence_type=None)
        default_double = AttrDefault(lambda value: value * 2, pass_key=True)
        self.assertRaises(AttributeError, lambda: default_none.foo)
        self.assertRaises(KeyError, lambda: default_none['foo'])
        self.assertEqual(default_none, {})

        self.assertEqual(default_list.foo, [])
        self.assertEqual(default_list['bar'], [])
        self.assertEqual(default_list, {'foo': [], 'bar': []})

        self.assertEqual(default_double.foo, 'foofoo')
        self.assertEqual(default_double['bar'], 'barbar')
        self.assertEqual(default_double, {'foo': 'foofoo', 'bar': 'barbar'})

    def test_repr(self):
        """
        repr(AttrDefault)
        """
        from attrdict.default import AttrDefault

        self.assertEqual(repr(AttrDefault(None)), "AttrDefault(None, False, {})")

        # list's repr changes between python 2 and python 3
        type_or_class = 'type' if PY2 else 'class'

        self.assertEqual(
            repr(AttrDefault(list)),
            type_or_class.join(("AttrDefault(<", " 'list'>, False, {})"))
        )

        self.assertEqual(
            repr(AttrDefault(list, {'foo': 'bar'}, pass_key=True)),
            type_or_class.join(
                ("AttrDefault(<", " 'list'>, True, {'foo': 'bar'})")
            )
        )


if __name__ == '__main__':
    # 只需要替换这一行
    nose2.main()
