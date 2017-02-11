'''
A module implementing the observer pattern
https://en.wikipedia.org/wiki/Observer_pattern

'''


class Observable(object):

    def __init__(self):
        self._observers = set()

    @property
    def observers(self):
        return self._observers

    def register_observer(self, observer):
        self._observers.add(observer)

    def notify_observers(self, event=None):
        for obs in self._observers:
            obs.notify(event)


class Observer(object):

    def notify(self, event):
        raise NotImplementedError()


if __name__ == '__main__':
    observable = Observable()
    observer = Observer()

    observable.register_observer(observer)

    observable.notify_observers()

