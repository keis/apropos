from about import Tracker
import unittest

states = ('foo', 'bar', 'baz')
sentinel_a = object()
sentinel_b = object()

class TestCollection(unittest.TestCase):

    def test_set_states_adds_to_all(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('bar', sentinel_b)
        a.set_state('baz', sentinel_b)
        self.assertEqual({sentinel_a, sentinel_b}, set(a.all))

    def test_clear_removes_from_all(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('bar', sentinel_b)
        a.set_state('baz', sentinel_b)
        a.clear_state('foo', sentinel_a)
        a.clear_state('baz', sentinel_b)
        self.assertEqual({sentinel_b}, set(a.all))

    def test_in_state_yield_objects_added(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('bar', sentinel_b)
        self.assertEqual({sentinel_a}, set(a.in_state('foo')))


class TestCheck(unittest.TestCase):

    def test_in_state_check(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('bar', sentinel_b)
        self.assertFalse(a.in_state('bar', sentinel_a))
        self.assertTrue(a.in_state('foo', sentinel_a))

    def test_none_is_not_in_state(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        self.assertFalse(a.in_state('foo', None))

    def test_is_alias(self):

        class Foo(Tracker):
            is_cool_for_cats = Tracker.is_alias('foo')

        a = Foo(states)
        a.set_state('foo', sentinel_a)
        self.assertTrue(a.is_cool_for_cats(sentinel_a))
        self.assertFalse(a.is_cool_for_cats(sentinel_b))


class TestHandle(unittest.TestCase):

    def test_state_check(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a, 'F')
        a.set_state('bar', sentinel_b)
        ast = a.about(sentinel_a)
        bst = a.about(sentinel_b)
        self.assertTrue(ast.foo)
        self.assertFalse(bst.foo)

    def test_state_set(self):
        a = Tracker(states)
        ast = a.about(sentinel_a)
        ast.foo = True
        self.assertTrue(a.in_state('foo', sentinel_a))

    def test_state_updates(self):
        a = Tracker(states)
        ast = a.about(sentinel_a)
        self.assertFalse(ast.bar)
        a.set_state('bar', sentinel_a)
        self.assertTrue(ast.bar)
