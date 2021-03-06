'''
A module implementing the observer pattern
https://en.wikipedia.org/wiki/Observer_pattern

'''

from multiprocessing import Queue
from threading import Thread


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


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, data):
        self.calls.append(data)

    @property
    def call_set(self):
        return set(self.calls)


class ProcessSafeRememberingObserver(Observer):
    def __init__(self):
        super(ProcessSafeRememberingObserver, self).__init__()
        self.calls = []
        self.q = Queue()
        self.worker = Thread(target=self.worker)
        self.worker.start()

    def notify(self, event):
        self.q.put(event)

    def stop(self):
        self.q.put(None)
        self.worker.join()

    def worker(self):
        while True:
            event = self.q.get()
            if event:
                self.calls.append(event)
            else:
                return

    @property
    def call_set(self):
        return set(self.calls)


if __name__ == '__main__':
    observable = Observable()
    observer = Observer()

    observable.register_observer(observer)

    observable.notify_observers()

