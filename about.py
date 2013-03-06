'''Generic state tracker with persistance.'''

import json


class Storage(object):
    '''Storage handle

    Each storage is associated with a filename where the data will be read
    and written to. It's possible to provide custom JSON encoder/decoders and
    it is  is *requried* if the state data or terms are not basic types.
    '''

    def __init__(self, file, encoder=None, decoder=None):
        '''Initialise a storage handle

        specify the JSON encoder/decoder to use by passing `encoder` and
        `decoder` respectivly.
        '''

        self.file = file
        self.encoder = encoder
        self.decoder = decoder

    def save(self, all, state):
        '''Writes the state serialised to JSON to file.

        The structure of the serialised data differs from the in memory
        tracking by making the tracked objects primary. Each term's associated
        subset of the state is attached. This is done to allow for
        sharding of the storage (not implemented) without getting any partial
        data.
        '''

        def row(item):
            return {
                'item': item,
                'state': dict(
                    ((k, v[item]) for k, v in state.items() if item in v))
            }

        with open(self.file, 'w') as f:
            json.dump([row(a) for a in all], f, cls=self.encoder)

    def load(self):
        '''Load the state from file.

        Each item and it's associted state will be generated by calling this
        method.
        '''

        with open(self.file, 'r') as f:
            for row in json.load(f, cls=self.decoder):
                yield (row['item'], row['state'])


class Tracker(object):
    '''Generic state tracker.

    Track state of objects, each state may have any data associated making
    this class usable as a glorified dictionary.
    '''

    # sentinel
    __no_term = object()

    @classmethod
    def is_alias(cls, state):
        '''Create a function that can be used as a alias for a in query.

            >>> class MyTracker(Tracker):
            ...     is_activated = Tracker.is_alias('active')
            ...
        '''
        return lambda self, obj: self.in_state(state, obj)

    def __init__(self, states, storage=None):
        self.states = tuple(states)
        self._states = dict(((s, {}) for s in states))
        self._storage = storage

        # Generate the handle class
        class Handle(object):
            for state in self.states:
                locals()[state] = property(
                    lambda w, s=state: self.in_state(s, w._obj),
                    lambda w, v, s=state: self.set_state(s, w._obj, v)
                )

            def __init__(self, obj):
                self._obj = obj

        self._about = Handle

    def load(self):
        '''Load state using the associated storage object.'''
        for obj, states in self._storage.load():
            for state, data in states.items():
                self.set_state(state, obj, data)

    def save(self):
        '''Save state using the associated storage object.'''
        self._storage.save(self.all, self._states)

    def about(self, obj):
        '''Create a handle for checking the state of the given object.'''
        return self._about(obj)

    @property
    def all(self):
        '''Set of all objects tracked.'''
        all = set()
        for state in self._states.values():
            # The terms are the keys of the state dictionary
            all.update(state)

        return all

    def set_state(self, state, obj, data=None):
        '''Set a object as being in a particular state.'''
        self._states[state][obj] = data

    def get_state(self, state, obj=__no_term):
        '''Get objects and data of state, or get object data from state

        When called with only state name this method will return a iterable
        with all objects and their associated data in that state. If a object
        is given in addition this method will return the associated data of
        that object in the named state.

        If the object is not in the named state KeyError will be raised.
        '''

        c = self._states[state]

        if obj is self.__no_term:
            return iter(c.items())

        return c[obj]

    def clear_state(self, state, obj=__no_term):
        '''Set a single object or all objects as not being in the named state.

        When called with only state name this method will set all objects
        currently in the named state as no longer being in the named state. If
        called with a object it sets that object as not being in the state.

        If the object is not in the named state no action is taken
        '''

        c = self._states[state]

        if obj is self.__no_term:
            self._states[state] = {}
            return

        if obj in c:
            del c[obj]

    def in_state(self, state, obj=__no_term):
        '''List objects in state, or check if a object is in that state

        When called with only state name this method will return a iterable
        with all objects in that state. If a object is given in addition this
        method will return True if that object is in the named state.
        '''

        c = self._states[state]

        if obj is self.__no_term:
            return c.keys()

        return obj in c

    def pop_state(self, state, obj):
        '''Set a object as not being in a particular state and return value.

        If the object is not in the named state KeyError will be raised.
        '''
        return self._states[state].pop(obj)

    def filter_state(self, state, key=lambda t, v: v):
        '''Removed terms from state as decided by key function

        If no key function is given this method will remove any term which
        associated data is falsy.

        A iterable of removed keys is returned.
        '''

        c = self._states[state]
        clear = [k for (k,v) in c.items() if not key(k, v)]
        for key in clear:
            del c[key]
        return clear

if __name__ == '__main__':
    about = Tracker(('spam', 'egg'), Storage('test.json'))
    a, b, c = 'abc'

    about.set_state('spam', a)
    about.set_state('spam', b, {'key': 'value'})
    about.set_state('egg', c)
    about.save()

    about2 = Tracker(('spam', 'egg'), Storage('test.json'))
    about2.load()
    print(about2.about(a).spam)
