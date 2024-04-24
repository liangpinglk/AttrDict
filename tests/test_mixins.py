"""
Tests for the AttrDefault class.
"""
import unittest

import nose2


class TestMixins(unittest.TestCase):

    def test_invalid_attributes(self):
        """
        Tests how set/delattr handle invalid attributes.
        """
        from attrdict.mapping import AttrMap

        mapping = AttrMap()

        # mapping currently has allow_invalid_attributes set to False
        def assign():
            """
            Assign to an invalid attribute.
            """
            mapping._key = 'value'

        self.assertRaises(TypeError, assign)
        self.assertRaises(AttributeError, lambda: mapping._key)
        self.assertEqual(mapping, {})

        mapping._setattr('_allow_invalid_attributes', True)

        assign()
        self.assertEqual(mapping._key, 'value')
        self.assertEqual(mapping, {})

        # delete the attribute
        def delete():
            """
            Delete an invalid attribute.
            """
            del mapping._key

        delete()
        self.assertRaises(AttributeError, lambda: mapping._key)
        self.assertEqual(mapping, {})

        # now with disallowing invalid
        assign()
        mapping._setattr('_allow_invalid_attributes', False)

        self.assertRaises(TypeError, delete)
        self.assertEqual(mapping._key, 'value')
        self.assertEqual(mapping, {})

        # force delete
        mapping._delattr('_key')
        self.assertRaises(AttributeError, lambda: mapping._key)
        self.assertEqual(mapping, {})

    def test_constructor(self):
        """
        _constructor MUST be implemented.
        """
        from attrdict.mixins import Attr

        class AttrImpl(Attr):
            """
            An implementation of attr that doesn't implement _constructor.
            """
            pass

        self.assertRaises(NotImplementedError, lambda: AttrImpl._constructor({}, ()))


if __name__ == '__main__':
    nose2.main()
