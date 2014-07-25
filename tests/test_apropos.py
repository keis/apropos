from apropos import Tracker, UnknownState
import unittest

states = ('foo', 'bar', 'baz')
sentinel_a = object()
sentinel_b = object()
sentinel_c = object()


class TestSetGet(unittest.TestCase):
    def test_set_get_value(self):
        data = object()
        a = Tracker(states)
        a.set_state('foo', sentinel_a, data)
        v = a.get_state('foo', sentinel_a)
        self.assertIs(data, v)

    def test_set_pop_value(self):
        data = object()
        a = Tracker(states)
        a.set_state('foo', sentinel_a, data)
        v = a.pop_state('foo', sentinel_a)
        self.assertIs(data, v)

    def test_pop_raises(self):
        a = Tracker(states)
        with self.assertRaises(KeyError):
            a.pop_state('foo', sentinel_a)

    def test_get_invalid(self):
        a = Tracker(states)
        with self.assertRaises(UnknownState):
            a.get_state('flurb', sentinel_a)


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

    def test_pop_removes_from_all(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('foo', sentinel_b)
        a.pop_state('foo', sentinel_a)
        self.assertEqual({sentinel_b}, set(a.all))

    def test_in_state_yield_objects_added(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('bar', sentinel_b)
        self.assertEqual({sentinel_a}, set(a.in_state('foo')))

    def test_get_state_enumerates_state(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('foo', sentinel_b)

        l = list(a.get_state('foo'))
        self.assertEqual(
            {(sentinel_a, None), (sentinel_b, None)},
            set(l)
        )

    def test_clear_state_resets(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('foo', sentinel_b)

        a.clear_state('foo')
        self.assertEqual(len(a.in_state('foo')), 0)

    def test_filter_removes_falsy_value(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a, True)
        a.set_state('foo', sentinel_b, False)
        a.set_state('foo', sentinel_c)

        a.filter_state('foo')
        self.assertEqual({sentinel_a}, set(a.in_state('foo')))

    def test_filter_custom_key(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a, 2)
        a.set_state('foo', sentinel_b, 3)
        a.set_state('foo', sentinel_c, 4)

        a.filter_state('foo', lambda t, v: v > 2)
        self.assertEqual({sentinel_b, sentinel_c}, set(a.in_state('foo')))

    def test_filter_yields_removed(self):
        a = Tracker(states)
        a.set_state('foo', sentinel_a)
        a.set_state('foo', sentinel_b)
        a.set_state('foo', sentinel_c, True)

        removed = list(a.filter_state('foo'))
        self.assertEqual({sentinel_a, sentinel_b}, set(removed))


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
