# encoding: UTF-8
"""
Tests for the AttrDict class.
"""
import unittest

import nose2
from six import PY2


class TestAttrDict(unittest.TestCase):

    def test_init(self):
        """
        Create a new AttrDict.
        """
        from attrdict.dictionary import AttrDict

        # empty
        self.assertEqual(AttrDict(), {})
        self.assertEqual(AttrDict(()), {})
        self.assertEqual(AttrDict({}), {})

        # with items
        self.assertEqual(AttrDict({'foo': 'bar'}), {'foo': 'bar'})
        self.assertEqual(AttrDict((('foo', 'bar'),)), {'foo': 'bar'})
        self.assertEqual(AttrDict(foo='bar'), {'foo': 'bar'})

        # non-overlapping
        self.assertEqual(AttrDict({}, foo='bar'), {'foo': 'bar'})
        self.assertEqual(AttrDict((), foo='bar'), {'foo': 'bar'})

        self.assertEqual(
            AttrDict({'alpha': 'bravo'}, foo='bar'),
            {'foo': 'bar', 'alpha': 'bravo'}
        )

        self.assertEqual(
            AttrDict((('alpha', 'bravo'),), foo='bar'),
            {'foo': 'bar', 'alpha': 'bravo'}
        )

        # updating
        self.assertEqual(
            AttrDict({'alpha': 'bravo'}, foo='bar', alpha='beta'),
            {'foo': 'bar', 'alpha': 'beta'}
        )

        self.assertEqual(
            AttrDict((('alpha', 'bravo'), ('alpha', 'beta')), foo='bar'),
            {'foo': 'bar', 'alpha': 'beta'}
        )

        self.assertEqual(
            AttrDict((('alpha', 'bravo'), ('alpha', 'beta')), alpha='bravo'),
            {'alpha': 'bravo'}
        )

    def test_copy(self):
        """
        Make a dict copy of an AttrDict.
        """
        from attrdict.dictionary import AttrDict

        mapping_a = AttrDict({'foo': {'bar': 'baz'}})
        mapping_b = mapping_a.copy()
        mapping_c = mapping_b

        mapping_b['foo']['lorem'] = 'ipsum'

        self.assertEqual(mapping_a, mapping_b)
        self.assertEqual(mapping_b, mapping_c)

    def test_fromkeys(self):
        """
        make a new sequence from a set of keys.
        """
        from attrdict.dictionary import AttrDict

        # default value
        self.assertEqual(AttrDict.fromkeys(()), {})
        self.assertEqual(
            AttrDict.fromkeys({'foo': 'bar', 'baz': 'qux'}),
            {'foo': None, 'baz': None}
        )
        self.assertEqual(
            AttrDict.fromkeys(('foo', 'baz')),
            {'foo': None, 'baz': None}
        )

        # custom value
        self.assertEqual(AttrDict.fromkeys((), 0), {})
        self.assertEqual(
            AttrDict.fromkeys({'foo': 'bar', 'baz': 'qux'}, 0),
            {'foo': 0, 'baz': 0}
        )
        self.assertEqual(
            AttrDict.fromkeys(('foo', 'baz'), 0),
            {'foo': 0, 'baz': 0}
        )

    def test_repr(self):
        """
        repr(AttrDict)
        """
        from attrdict.dictionary import AttrDict

        self.assertEqual(repr(AttrDict()), "AttrDict({})")
        self.assertEqual(repr(AttrDict({'foo': 'bar'})), "AttrDict({'foo': 'bar'})")
        self.assertEqual(
            repr(AttrDict({1: {'foo': 'bar'}})), "AttrDict({1: {'foo': 'bar'}})"
        )
        self.assertEqual(
            repr(AttrDict({1: AttrDict({'foo': 'bar'})})),
            "AttrDict({1: AttrDict({'foo': 'bar'})})"
        )

    def test_has_key(self):
        """
        The now-depricated has_keys method
        """
        if not PY2:
            from attrdict.dictionary import AttrDict

            self.assertFalse(hasattr(AttrDict(), 'has_key'))


if __name__ == '__main__':
    nose2.main()
