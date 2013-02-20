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
            json.dump([ row(a) for a in all ], f)

    def load(self):
        with open(self.file, 'r') as f:
            for row in json.load(f):
                yield (row['item'], row['state'])


class Tracker(object):
    __list_state = object()

    @classmethod
    def is_alias(cls, state):
        return lambda self, obj: self.in_state(state, obj)

    def __init__(self, states, storage = None):
        self.states = tuple(states)
        self._states = dict(((s, {}) for s in states))
        self._storage = storage

        class Handle(object):
            for state in self.states:
                locals()[state] = property(
                    lambda w, s = state: self.in_state(s, w._obj),
                    lambda w, v, s = state: self.set_state(s, w._obj, v)
                )

            def __init__(self, obj):
                self._obj = obj

        self._about = Handle

    def load(self):
        for obj, states in self._storage.load():
            for state, data in states.items():
                self.set_state(state, obj, data)

    def save(self):
        self._storage.save(self.all, self._states)

    def about(self, obj):
        return self._about(obj)

    @property
    def all(self):
        all = set()
        for state in self._states.values():
            all.update(state)

        return all

    def set_state(self, state, obj, data = None):
        self._states[state][obj] = data

    def get_state(self, state, obj):
        return self._states[state][obj]

    def clear_state(self, state, obj):
        c = self._states[state]
        if obj in c:
            del c[obj]

    def in_state(self, state, obj = __list_state):
        c = self._states[state]
        if obj is self.__list_state:
            return c.keys()
        return obj in c


if __name__ == '__main__':
    about = Tracker(('spam', 'egg'), Storage('test.json'))
    a, b, c = 'abc'

    about.set_state('spam', a)
    about.set_state('spam', b, {'key': 'value'})
    about.set_state('egg', c)
    about.save()

    about2 = Tracker(('spam', 'egg'), Storage('test.json'))
    about2.load()
    print about2.about(a).spam
