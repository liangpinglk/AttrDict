"""
Test the merge function
"""
import unittest

import nose2


class TestMerge(unittest.TestCase):
    def test_merge(self):
        """
        merge function.
        """
        from attrdict.merge import merge

        left = {
            'baz': 'qux',
            'mismatch': False,
            'sub': {'alpha': 'beta', 1: 2},
        }
        right = {
            'lorem': 'ipsum',
            'mismatch': True,
            'sub': {'alpha': 'bravo', 3: 4},
        }

        self.assertEqual(merge({}, {}), {})
        self.assertEqual(merge(left, {}), left)
        self.assertEqual(merge({}, right), right)
        self.assertEqual(
            merge(left, right),
            {
                'baz': 'qux',
                'lorem': 'ipsum',
                'mismatch': True,
                'sub': {'alpha': 'bravo', 1: 2, 3: 4}
            }
        )


if __name__ == '__main__':
    nose2.main()
