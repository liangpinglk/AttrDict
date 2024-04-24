# encoding: UTF-8
"""
Common tests that apply to multiple Attr-derived classes.
"""
import copy
import unittest
from collections.abc import Mapping, ItemsView, KeysView, ValuesView
from dataclasses import dataclass
from itertools import chain
import pickle
from sys import version_info
from typing import NamedTuple

import nose2
import six

from attrdict.mixins import Attr


# Options = NamedTuple(
#     'Options',
#     ('cls', 'constructor', 'mutable', 'iter_methods', 'view_methods',
#      'recursive')
# )


@dataclass
class Options:
    cls: str
    constructor: str
    mutable: bool
    iter_methods: list
    view_methods: list
    recursive: bool


class AttrImpl(Attr):
    """
    An implementation of Attr.
    """

    def __init__(self, items=None, sequence_type=tuple):
        if items is None:
            items = {}
        elif not isinstance(items, Mapping):
            items = dict(items)

        self._mapping = items
        self._sequence_type = sequence_type

    def _configuration(self):
        """
        The configuration for an attrmap instance.
        """
        return self._sequence_type

    def __getitem__(self, key):
        """
        Access a value associated with a key.
        """
        return self._mapping[key]

    def __len__(self):
        """
        Check the length of the mapping.
        """
        return len(self._mapping)

    def __iter__(self):
        """
        Iterated through the keys.
        """
        return iter(self._mapping)

    def __getstate__(self):
        """
        Serialize the object.
        """
        return (self._mapping, self._sequence_type)

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        mapping, sequence_type = state
        self._mapping = mapping
        self._sequence_type = sequence_type

    @classmethod
    def _constructor(cls, mapping, configuration):
        """
        A standardized constructor.
        """
        return cls(mapping, sequence_type=configuration)


class TestCommon(unittest.TestCase):
    def test_attr(self):
        """
        Tests for an class that implements Attr.
        """
        for test in self.common(AttrImpl, mutable=False):
            yield test

    def test_attrmap(self):
        """
        Run AttrMap against the common tests.
        """
        from attrdict.mapping import AttrMap

        for test in self.common(AttrMap, mutable=True):
            yield test

    def test_attrdict(self):
        """
        Run AttrDict against the common tests.
        """
        from attrdict.dictionary import AttrDict

        view_methods = (2, 7) <= version_info < (3,)

        def constructor(items=None, sequence_type=tuple):
            """
            Build a new AttrDict.
            """
            if items is None:
                items = {}

            return AttrDict._constructor(items, sequence_type)

        for test in self.common(AttrDict, constructor=constructor,
                                mutable=True, iter_methods=True,
                                view_methods=view_methods, recursive=False):
            yield test

    def test_attrdefault(self):
        """
        Run AttrDefault against the common tests.
        """
        from attrdict.default import AttrDefault

        def constructor(items=None, sequence_type=tuple):
            """
            Build a new AttrDefault.
            """
            if items is None:
                items = {}

            return AttrDefault(None, items, sequence_type)

        for test in self.common(AttrDefault, constructor=constructor, mutable=True):
            yield test

    def common(self, cls, constructor=None, mutable=False, iter_methods=False,
               view_methods=False, recursive=True):
        """
        Iterates over tests common to multiple Attr-derived classes
    
        cls: The class that is being tested.
        mutable: (optional, False) Whether the object is supposed to be
            mutable.
        iter_methods: (optional, False) Whether the class implements
            iter<keys,values,items> under Python 2.
        view_methods: (optional, False) Whether the class implements
            view<keys,values,items> under Python 2.
        recursive: (optional, True) Whether recursive assignment works.
        """
        tests = (
            self.item_access, self.iteration, self.containment, self.length, self.equality,
            self.item_creation, self.item_deletion, self.sequence_typing, self.addition,
            self.to_kwargs, self.pickling,
        )

        mutable_tests = (
            self.pop, self.popitem, self.clear, self.update, self.setdefault, self.copying, self.deepcopying,
        )

        if constructor is None:
            constructor = cls

        options = Options(cls, constructor, mutable, iter_methods, view_methods,
                          recursive)

        if mutable:
            tests = chain(tests, mutable_tests)

        for test in tests:
            # test.description = test.__doc__.format(cls=cls.__name__)

            yield test, options

    def item_access(self, options):
        """Access items in {cls}."""
        mapping = options.constructor(
            {
                'foo': 'bar',
                '_lorem': 'ipsum',
                six.u('👻'): 'boo',
                3: 'three',
                'get': 'not the function',
                'sub': {'alpha': 'bravo'},
                'bytes': b'bytes',
                'tuple': ({'a': 'b'}, 'c'),
                'list': [{'a': 'b'}, {'c': 'd'}],
            }
        )

        # key that can be an attribute
        self.assertEqual(mapping['foo'], 'bar')
        self.assertEqual(mapping.foo, 'bar')
        self.assertEqual(mapping('foo'), 'bar')
        self.assertEqual(mapping.get('foo'), 'bar')

        # key that cannot be an attribute
        self.assertEqual(mapping[3], 'three')
        self.assertRaises(TypeError, getattr, mapping, 3)
        self.assertEqual(mapping(3), 'three')
        self.assertEqual(mapping.get(3), 'three')

        # key that cannot be an attribute (sadly)
        self.assertEqual(mapping[six.u('👻')], 'boo')
        if six.PY2:
            self.assertRaises(UnicodeEncodeError, getattr, mapping, six.u('👻'))
        else:
            self.assertRaises(AttributeError, getattr, mapping, six.u('👻'))
        self.assertEqual(mapping(six.u('👻')), 'boo')
        self.assertEqual(mapping.get(six.u('👻')), 'boo')

        # key that represents a hidden attribute
        self.assertEqual(mapping['_lorem'], 'ipsum')
        self.assertRaises(AttributeError, lambda: mapping._lorem)
        self.assertEqual(mapping('_lorem'), 'ipsum')
        self.assertEqual(mapping.get('_lorem'), 'ipsum')

        # key that represents an attribute that already exists
        self.assertEqual(mapping['get'], 'not the function')
        self.assertNotEqual(mapping.get, 'not the function')
        self.assertEqual(mapping('get'), 'not the function')
        self.assertEqual(mapping.get('get'), 'not the function')

        # does recursion work
        self.assertRaises(AttributeError, lambda: mapping['sub'].alpha)
        self.assertEqual(mapping.sub.alpha, 'bravo')
        self.assertEqual(mapping('sub').alpha, 'bravo')
        self.assertRaises(AttributeError, lambda: mapping.get('sub').alpha)

        # bytes
        self.assertEqual(mapping['bytes'], b'bytes')
        self.assertEqual(mapping.bytes, b'bytes')
        self.assertEqual(mapping('bytes'), b'bytes')
        self.assertEqual(mapping.get('bytes'), b'bytes')

        # tuple
        self.assertEqual(mapping['tuple'], ({'a': 'b'}, 'c'))
        self.assertEqual(mapping.tuple, ({'a': 'b'}, 'c'))
        self.assertEqual(mapping('tuple'), ({'a': 'b'}, 'c'))
        self.assertEqual(mapping.get('tuple'), ({'a': 'b'}, 'c'))

        self.assertRaises(AttributeError, lambda: mapping['tuple'][0].a)
        self.assertEqual(mapping.tuple[0].a, 'b')
        self.assertEqual(mapping('tuple')[0].a, 'b')
        self.assertRaises(AttributeError, lambda: mapping.get('tuple')[0].a)

        self.true = self.assertTrue
        self.true(isinstance(mapping['tuple'], tuple))
        self.assertTrue(isinstance(mapping.tuple, tuple))
        self.assertTrue(isinstance(mapping('tuple'), tuple))
        self.assertTrue(isinstance(mapping.get('tuple'), tuple))

        self.assertTrue(isinstance(mapping['tuple'][0], dict))
        self.assertTrue(isinstance(mapping.tuple[0], options.cls))
        self.assertTrue(isinstance(mapping('tuple')[0], options.cls))
        self.assertTrue(isinstance(mapping.get('tuple')[0], dict))

        self.assertTrue(isinstance(mapping['tuple'][1], str))
        self.assertTrue(isinstance(mapping.tuple[1], str))
        self.assertTrue(isinstance(mapping('tuple')[1], str))
        self.assertTrue(isinstance(mapping.get('tuple')[1], str))

        # list
        self.assertEqual(mapping['list'], [{'a': 'b'}, {'c': 'd'}])
        self.assertEqual(mapping.list, ({'a': 'b'}, {'c': 'd'}))
        self.assertEqual(mapping('list'), ({'a': 'b'}, {'c': 'd'}))
        self.assertEqual(mapping.get('list'), [{'a': 'b'}, {'c': 'd'}])

        self.assertRaises(AttributeError, lambda: mapping['list'][0].a)
        self.assertEqual(mapping.list[0].a, 'b')
        self.assertEqual(mapping('list')[0].a, 'b')
        self.assertRaises(AttributeError, lambda: mapping.get('list')[0].a)

        self.assertTrue(isinstance(mapping['list'], list))
        self.assertTrue(isinstance(mapping.list, tuple))
        self.assertTrue(isinstance(mapping('list'), tuple))
        self.assertTrue(isinstance(mapping.get('list'), list))

        self.assertTrue(isinstance(mapping['list'][0], dict))
        self.assertTrue(isinstance(mapping.list[0], options.cls))
        self.assertTrue(isinstance(mapping('list')[0], options.cls))
        self.assertTrue(isinstance(mapping.get('list')[0], dict))

        self.assertTrue(isinstance(mapping['list'][1], dict))
        self.assertTrue(isinstance(mapping.list[1], options.cls))
        self.assertTrue(isinstance(mapping('list')[1], options.cls))
        self.assertTrue(isinstance(mapping.get('list')[1], dict))

        # Nonexistent key
        self.assertRaises(KeyError, lambda: mapping['fake'])
        self.assertRaises(AttributeError, lambda: mapping.fake)
        self.assertRaises(AttributeError, lambda: mapping('fake'))
        self.assertEqual(mapping.get('fake'), None)
        self.assertEqual(mapping.get('fake', 'bake'), 'bake')

    def iteration(self, options):
        "Iterate over keys/values/items in {cls}"
        raw = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'bravo'}

        mapping = options.constructor(raw)

        expected_keys = frozenset(('foo', 'lorem', 'alpha'))
        expected_values = frozenset(('bar', 'ipsum', 'bravo'))
        expected_items = frozenset(
            (('foo', 'bar'), ('lorem', 'ipsum'), ('alpha', 'bravo'))
        )

        self.assertEqual(set(iter(mapping)), expected_keys)

        actual_keys = mapping.keys()
        actual_values = mapping.values()
        actual_items = mapping.items()

        if six.PY2:
            for collection in (actual_keys, actual_values, actual_items):
                self.assertTrue(isinstance(collection, list))

            self.assertEqual(frozenset(actual_keys), expected_keys)
            self.assertEqual(frozenset(actual_values), expected_values)
            self.assertEqual(frozenset(actual_items), expected_items)

            if options.iter_methods:
                actual_keys = mapping.iterkeys()
                actual_values = mapping.itervalues()
                actual_items = mapping.iteritems()

                for iterable in (actual_keys, actual_values, actual_items):
                    self.assertFalse(isinstance(iterable, list))

                self.assertEqual(frozenset(actual_keys), expected_keys)
                self.assertEqual(frozenset(actual_values), expected_values)
                self.assertEqual(frozenset(actual_items), expected_items)

            if options.view_methods:
                actual_keys = mapping.viewkeys()
                actual_values = mapping.viewvalues()
                actual_items = mapping.viewitems()

                # These views don't actually extend from collections.abc.*View
                for iterable in (actual_keys, actual_values, actual_items):
                    self.assertFalse(isinstance(iterable, list))

                self.assertEqual(frozenset(actual_keys), expected_keys)
                self.assertEqual(frozenset(actual_values), expected_values)
                self.assertEqual(frozenset(actual_items), expected_items)

                # What happens if mapping isn't a dict
                from attrdict.mapping import AttrMap

                mapping = options.constructor(AttrMap(raw))

                actual_keys = mapping.viewkeys()
                actual_values = mapping.viewvalues()
                actual_items = mapping.viewitems()

                # These views don't actually extend from collections.abc.*View
                for iterable in (actual_keys, actual_values, actual_items):
                    self.assertFalse(isinstance(iterable, list))

                self.assertEqual(frozenset(actual_keys), expected_keys)
                self.assertEqual(frozenset(actual_values), expected_values)
                self.assertEqual(frozenset(actual_items), expected_items)

        else:  # methods are actually views
            self.assertTrue(isinstance(actual_keys, KeysView))
            self.assertEqual(frozenset(actual_keys), expected_keys)

            self.assertTrue(isinstance(actual_values, ValuesView))
            self.assertEqual(frozenset(actual_values), expected_values)

            self.assertTrue(isinstance(actual_items, ItemsView))
            self.assertEqual(frozenset(actual_items), expected_items)

        # make sure empty iteration works
        self.assertEqual(tuple(options.constructor().items()), ())

    def containment(self, options):
        "Check whether {cls} contains keys"
        mapping = options.constructor(
            {'foo': 'bar', frozenset((1, 2, 3)): 'abc', 1: 2}
        )
        empty = options.constructor()

        self.assertTrue('foo' in mapping)
        self.assertFalse('foo' in empty)

        self.assertTrue(frozenset((1, 2, 3)) in mapping)
        self.assertFalse(frozenset((1, 2, 3)) in empty)

        self.assertTrue(1 in mapping)
        self.assertFalse(1 in empty)

        self.assertFalse('banana' in mapping)
        self.assertFalse('banana' in empty)

    def length(self, options):
        "Get the length of an {cls} instance"
        self.assertEqual(len(options.constructor()), 0)
        self.assertEqual(len(options.constructor({'foo': 'bar'})), 1)
        self.assertEqual(len(options.constructor({'foo': 'bar', 'baz': 'qux'})), 2)

    def equality(self, options):
        "Equality checks for {cls}"
        empty = {}
        mapping_a = {'foo': 'bar'}
        mapping_b = {'lorem': 'ipsum'}

        constructor = options.constructor

        self.assertTrue(constructor(empty) == empty)
        self.assertFalse(constructor(empty) != empty)
        self.assertFalse(constructor(empty) == mapping_a)
        self.assertTrue(constructor(empty) != mapping_a)
        self.assertFalse(constructor(empty) == mapping_b)
        self.assertTrue(constructor(empty) != mapping_b)

        self.assertFalse(constructor(mapping_a) == empty)
        self.assertTrue(constructor(mapping_a) != empty)
        self.assertTrue(constructor(mapping_a) == mapping_a)
        self.assertFalse(constructor(mapping_a) != mapping_a)
        self.assertFalse(constructor(mapping_a) == mapping_b)
        self.assertTrue(constructor(mapping_a) != mapping_b)

        self.assertFalse(constructor(mapping_b) == empty)
        self.assertTrue(constructor(mapping_b) != empty)
        self.assertFalse(constructor(mapping_b) == mapping_a)
        self.assertTrue(constructor(mapping_b) != mapping_a)
        self.assertTrue(constructor(mapping_b) == mapping_b)
        self.assertFalse(constructor(mapping_b) != mapping_b)

        self.assertTrue(constructor(empty) == constructor(empty))
        self.assertFalse(constructor(empty) != constructor(empty))
        self.assertFalse(constructor(empty) == constructor(mapping_a))
        self.assertTrue(constructor(empty) != constructor(mapping_a))
        self.assertFalse(constructor(empty) == constructor(mapping_b))
        self.assertTrue(constructor(empty) != constructor(mapping_b))

        self.assertFalse(constructor(mapping_a) == constructor(empty))
        self.assertTrue(constructor(mapping_a) != constructor(empty))
        self.assertTrue(constructor(mapping_a) == constructor(mapping_a))
        self.assertFalse(constructor(mapping_a) != constructor(mapping_a))
        self.assertFalse(constructor(mapping_a) == constructor(mapping_b))
        self.assertTrue(constructor(mapping_a) != constructor(mapping_b))

        self.assertFalse(constructor(mapping_b) == constructor(empty))
        self.assertTrue(constructor(mapping_b) != constructor(empty))
        self.assertFalse(constructor(mapping_b) == constructor(mapping_a))
        self.assertTrue(constructor(mapping_b) != constructor(mapping_a))
        self.assertTrue(constructor(mapping_b) == constructor(mapping_b))
        self.assertFalse(constructor(mapping_b) != constructor(mapping_b))

        self.assertTrue(constructor((('foo', 'bar'),)) == {'foo': 'bar'})

    def item_creation(self, options):
        "Add a key-value pair to an {cls}"

        if not options.mutable:
            # Assignment shouldn't add to the dict
            mapping = options.constructor()

            try:
                mapping.foo = 'bar'
            except TypeError:
                pass  # may fail if setattr modified
            else:
                pass  # may assign, but shouldn't assign to dict

            def item():
                """
                Attempt to add an item.
                """
                mapping['foo'] = 'bar'

            self.assertRaises(TypeError, item)

            self.assertFalse('foo' in mapping)
        else:
            mapping = options.constructor()

            # key that can be an attribute
            mapping.foo = 'bar'

            self.assertEqual(mapping.foo, 'bar')
            self.assertEqual(mapping['foo'], 'bar')
            self.assertEqual(mapping('foo'), 'bar')
            self.assertEqual(mapping.get('foo'), 'bar')

            mapping['baz'] = 'qux'

            self.assertEqual(mapping.baz, 'qux')
            self.assertEqual(mapping['baz'], 'qux')
            self.assertEqual(mapping('baz'), 'qux')
            self.assertEqual(mapping.get('baz'), 'qux')

            # key that cannot be an attribute
            self.assertRaises(TypeError, setattr, mapping, 1, 'one')

            self.assertTrue(1 not in mapping)

            mapping[2] = 'two'

            self.assertEqual(mapping[2], 'two')
            self.assertEqual(mapping(2), 'two')
            self.assertEqual(mapping.get(2), 'two')

            # key that represents a hidden attribute
            def add_foo():
                "add _foo to mapping"
                mapping._foo = '_bar'

            self.assertRaises(TypeError, add_foo)
            self.assertFalse('_foo' in mapping)

            mapping['_baz'] = 'qux'

            def get_baz():
                "get the _foo attribute"
                return mapping._baz

            self.assertRaises(AttributeError, get_baz)
            self.assertEqual(mapping['_baz'], 'qux')
            self.assertEqual(mapping('_baz'), 'qux')
            self.assertEqual(mapping.get('_baz'), 'qux')

            # key that represents an attribute that already exists
            def add_get():
                "add get to mapping"
                mapping.get = 'attribute'

            self.assertRaises(TypeError, add_get)
            self.assertFalse('get' in mapping)

            mapping['get'] = 'value'

            self.assertNotEqual(mapping.get, 'value')
            self.assertEqual(mapping['get'], 'value')
            self.assertEqual(mapping('get'), 'value')
            self.assertEqual(mapping.get('get'), 'value')

            # rewrite a value
            mapping.foo = 'manchu'

            self.assertEqual(mapping.foo, 'manchu')
            self.assertEqual(mapping['foo'], 'manchu')
            self.assertEqual(mapping('foo'), 'manchu')
            self.assertEqual(mapping.get('foo'), 'manchu')

            mapping['bar'] = 'bell'

            self.assertEqual(mapping.bar, 'bell')
            self.assertEqual(mapping['bar'], 'bell')
            self.assertEqual(mapping('bar'), 'bell')
            self.assertEqual(mapping.get('bar'), 'bell')

            if options.recursive:
                recursed = options.constructor({'foo': {'bar': 'baz'}})

                recursed.foo.bar = 'qux'
                recursed.foo.alpha = 'bravo'

                self.assertEqual(recursed, {'foo': {'bar': 'qux', 'alpha': 'bravo'}})

    def item_deletion(self, options):
        "Remove a key-value from to an {cls}"
        if not options.mutable:
            mapping = options.constructor({'foo': 'bar'})

            # could be a TypeError or an AttributeError
            try:
                del mapping.foo
            except TypeError:
                pass
            except AttributeError:
                pass
            else:
                raise AssertionError('deletion should fail')

            def item(mapping):
                """
                Attempt to del an item
                """
                del mapping['foo']

            self.assertRaises(TypeError, item, mapping)

            self.assertEqual(mapping, {'foo': 'bar'})
            self.assertEqual(mapping.foo, 'bar')
            self.assertEqual(mapping['foo'], 'bar')
        else:
            mapping = options.constructor(
                {'foo': 'bar', 'lorem': 'ipsum', '_hidden': True, 'get': 'value'}
            )

            del mapping.foo
            self.assertFalse('foo' in mapping)

            del mapping['lorem']
            self.assertFalse('lorem' in mapping)

            def del_hidden():
                "delete _hidden"
                del mapping._hidden

            try:
                del_hidden()
            except KeyError:
                pass
            except TypeError:
                pass
            else:
                self.assertFalse("Test raised the appropriate exception")
            # self.assertRaises(TypeError, del_hidden)
            self.assertTrue('_hidden' in mapping)

            del mapping['_hidden']
            self.assertFalse('hidden' in mapping)

            def del_get():
                "delete get"
                del mapping.get

            self.assertRaises(TypeError, del_get)
            self.assertTrue('get' in mapping)
            self.assertTrue(mapping.get('get'), 'value')

            del mapping['get']
            self.assertFalse('get' in mapping)
            self.assertTrue(mapping.get('get', 'banana'), 'banana')

    def sequence_typing(self, options):
        "Does {cls} respect sequence type?"
        data = {'list': [{'foo': 'bar'}], 'tuple': ({'foo': 'bar'},)}

        tuple_mapping = options.constructor(data)

        self.assertTrue(isinstance(tuple_mapping.list, tuple))
        self.assertEqual(tuple_mapping.list[0].foo, 'bar')

        self.assertTrue(isinstance(tuple_mapping.tuple, tuple))
        self.assertEqual(tuple_mapping.tuple[0].foo, 'bar')

        list_mapping = options.constructor(data, sequence_type=list)

        self.assertTrue(isinstance(list_mapping.list, list))
        self.assertEqual(list_mapping.list[0].foo, 'bar')

        self.assertTrue(isinstance(list_mapping.tuple, list))
        self.assertEqual(list_mapping.tuple[0].foo, 'bar')

        none_mapping = options.constructor(data, sequence_type=None)

        self.assertTrue(isinstance(none_mapping.list, list))
        self.assertRaises(AttributeError, lambda: none_mapping.list[0].foo)

        self.assertTrue(isinstance(none_mapping.tuple, tuple))
        self.assertRaises(AttributeError, lambda: none_mapping.tuple[0].foo)

    def addition(self, options):
        "Adding {cls} to other mappings."
        left = {
            'foo': 'bar',
            'mismatch': False,
            'sub': {'alpha': 'beta', 'a': 'b'},
        }

        right = {
            'lorem': 'ipsum',
            'mismatch': True,
            'sub': {'alpha': 'bravo', 'c': 'd'},
        }

        merged = {
            'foo': 'bar',
            'lorem': 'ipsum',
            'mismatch': True,
            'sub': {'alpha': 'bravo', 'a': 'b', 'c': 'd'}
        }

        opposite = {
            'foo': 'bar',
            'lorem': 'ipsum',
            'mismatch': False,
            'sub': {'alpha': 'beta', 'a': 'b', 'c': 'd'}
        }

        constructor = options.constructor

        self.assertRaises(TypeError, lambda: constructor() + 1)
        self.assertRaises(TypeError, lambda: 1 + constructor())

        self.assertEqual(constructor() + constructor(), {})
        self.assertEqual(constructor() + {}, {})
        self.assertEqual({} + constructor(), {})

        self.assertEqual(constructor(left) + constructor(), left)
        self.assertEqual(constructor(left) + {}, left)
        self.assertEqual({} + constructor(left), left)

        self.assertEqual(constructor() + constructor(left), left)
        self.assertEqual(constructor() + left, left)
        self.assertEqual(left + constructor(), left)

        self.assertEqual(constructor(left) + constructor(right), merged)
        self.assertEqual(constructor(left) + right, merged)
        self.assertEqual(left + constructor(right), merged)

        self.assertEqual(constructor(right) + constructor(left), opposite)
        self.assertEqual(constructor(right) + left, opposite)
        self.assertEqual(right + constructor(left), opposite)

        # test sequence type changes
        data = {'sequence': [{'foo': 'bar'}]}

        self.assertTrue(isinstance((constructor(data) + {}).sequence, tuple))
        self.assertTrue(
            isinstance((constructor(data) + constructor()).sequence, tuple)
        )

        self.assertTrue(isinstance((constructor(data, list) + {}).sequence, list))
        # self.assertTrue(
        #     isinstance((constructor(data, list) + constructor()).sequence, tuple)
        # )

        self.assertTrue(isinstance((constructor(data, list) + {}).sequence, list))
        self.assertTrue(
            isinstance(
                (constructor(data, list) + constructor({}, list)).sequence,
                list
            )
        )

    def to_kwargs(self, options):
        "**{cls}"

        def return_results(**kwargs):
            "Return result passed into a function"
            return kwargs

        expected = {'foo': 1, 'bar': 2}

        self.assertEqual(return_results(**options.constructor()), {})
        self.assertEqual(return_results(**options.constructor(expected)), expected)

    def check_pickle_roundtrip(self, source, options, **kwargs):
        """
        serialize then deserialize a mapping, ensuring the result and initial
        objects are equivalent.
        """
        source = options.constructor(source, **kwargs)
        data = pickle.dumps(source)
        loaded = pickle.loads(data)

        self.assertTrue(isinstance(loaded, options.cls))

        self.assertEqual(source, loaded)

        return loaded

    def pickling(self, options):
        "Pickle {cls}"

        empty = self.check_pickle_roundtrip(None, options)
        self.assertEqual(empty, {})

        mapping = self.check_pickle_roundtrip({'foo': 'bar'}, options)
        self.assertEqual(mapping, {'foo': 'bar'})

        # make sure sequence_type is preserved
        raw = {'list': [{'a': 'b'}], 'tuple': ({'a': 'b'},)}

        as_tuple = self.check_pickle_roundtrip(raw, options)
        self.assertTrue(isinstance(as_tuple['list'], list))
        self.assertTrue(isinstance(as_tuple['tuple'], tuple))
        self.assertTrue(isinstance(as_tuple.list, tuple))
        self.assertTrue(isinstance(as_tuple.tuple, tuple))

        as_list = self.check_pickle_roundtrip(raw, options, sequence_type=list)
        self.assertTrue(isinstance(as_list['list'], list))
        self.assertTrue(isinstance(as_list['tuple'], tuple))
        self.assertTrue(isinstance(as_list.list, list))
        self.assertTrue(isinstance(as_list.tuple, list))

        as_raw = self.check_pickle_roundtrip(raw, options, sequence_type=None)
        self.assertTrue(isinstance(as_raw['list'], list))
        self.assertTrue(isinstance(as_raw['tuple'], tuple))
        self.assertTrue(isinstance(as_raw.list, list))
        self.assertTrue(isinstance(as_raw.tuple, tuple))

    def pop(self, options):
        "Popping from {cls}"

        mapping = options.constructor({'foo': 'bar', 'baz': 'qux'})

        self.assertRaises(KeyError, lambda: mapping.pop('lorem'))
        self.assertEqual(mapping.pop('lorem', 'ipsum'), 'ipsum')
        self.assertEqual(mapping, {'foo': 'bar', 'baz': 'qux'})

        self.assertEqual(mapping.pop('baz'), 'qux')
        self.assertFalse('baz' in mapping)
        self.assertEqual(mapping, {'foo': 'bar'})

        self.assertEqual(mapping.pop('foo', 'qux'), 'bar')
        self.assertFalse('foo' in mapping)
        self.assertEqual(mapping, {})

    def popitem(self, options):
        "Popping items from {cls}"
        expected = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'beta'}
        actual = {}

        mapping = options.constructor(dict(expected))

        for _ in range(3):
            key, value = mapping.popitem()

            self.assertEqual(expected[key], value)
            actual[key] = value

        self.assertEqual(expected, actual)

        self.assertRaises(AttributeError, lambda: mapping.foo)
        self.assertRaises(AttributeError, lambda: mapping.lorem)
        self.assertRaises(AttributeError, lambda: mapping.alpha)
        self.assertRaises(KeyError, mapping.popitem)

    def clear(self, options):
        "clear the {cls}"

        mapping = options.constructor(
            {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'beta'}
        )

        mapping.clear()

        self.assertEqual(mapping, {})

        self.assertRaises(AttributeError, lambda: mapping.foo)
        self.assertRaises(AttributeError, lambda: mapping.lorem)
        self.assertRaises(AttributeError, lambda: mapping.alpha)

    def update(self, options):
        "update a {cls}"

        mapping = options.constructor({'foo': 'bar', 'alpha': 'bravo'})

        mapping.update(alpha='beta', lorem='ipsum')
        self.assertEqual(mapping, {'foo': 'bar', 'alpha': 'beta', 'lorem': 'ipsum'})

        mapping.update({'foo': 'baz', 1: 'one'})
        self.assertEqual(
            mapping,
            {'foo': 'baz', 'alpha': 'beta', 'lorem': 'ipsum', 1: 'one'}
        )

        self.assertEqual(mapping.foo, 'baz')
        self.assertEqual(mapping.alpha, 'beta')
        self.assertEqual(mapping.lorem, 'ipsum')
        self.assertEqual(mapping(1), 'one')

    def setdefault(self, options):
        "{cls}.setdefault"

        mapping = options.constructor({'foo': 'bar'})

        self.assertEqual(mapping.setdefault('foo', 'baz'), 'bar')
        self.assertEqual(mapping.foo, 'bar')

        self.assertEqual(mapping.setdefault('lorem', 'ipsum'), 'ipsum')
        self.assertEqual(mapping.lorem, 'ipsum')

        self.assertTrue(mapping.setdefault('return_none') is None)
        self.assertTrue(mapping.return_none is None)

        self.assertEqual(mapping.setdefault(1, 'one'), 'one')
        self.assertEqual(mapping[1], 'one')

        self.assertEqual(mapping.setdefault('_hidden', 'yes'), 'yes')
        self.assertRaises(AttributeError, lambda: mapping._hidden)
        self.assertEqual(mapping['_hidden'], 'yes')

        self.assertEqual(mapping.setdefault('get', 'value'), 'value')
        self.assertNotEqual(mapping.get, 'value')
        self.assertEqual(mapping['get'], 'value')

    def copying(self, options):
        "copying a {cls}"
        mapping_a = options.constructor({'foo': {'bar': 'baz'}})
        mapping_b = copy.copy(mapping_a)
        mapping_c = mapping_b

        mapping_b.foo.lorem = 'ipsum'

        self.assertEqual(mapping_a, mapping_b)
        self.assertEqual(mapping_b, mapping_c)

        mapping_c.alpha = 'bravo'

    def deepcopying(self, options):
        "deepcopying a {cls}"
        mapping_a = options.constructor({'foo': {'bar': 'baz'}})
        mapping_b = copy.deepcopy(mapping_a)
        mapping_c = mapping_b

        mapping_b['foo']['lorem'] = 'ipsum'

        self.assertNotEqual(mapping_a, mapping_b)
        self.assertEqual(mapping_b, mapping_c)

        mapping_c.alpha = 'bravo'

        self.assertNotEqual(mapping_a, mapping_b)
        self.assertEqual(mapping_b, mapping_c)

        self.assertFalse('lorem' in mapping_a.foo)
        self.assertEqual(mapping_a.setdefault('alpha', 'beta'), 'beta')
        self.assertEqual(mapping_c.alpha, 'bravo')


if __name__ == '__main__':
    nose2.main()
