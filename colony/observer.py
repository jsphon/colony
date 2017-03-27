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
            print('Notifying observer %s'%obs)
            obs.notify(event)


class Observer(object):

    def notify(self, event):
        raise NotImplementedError()


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event.payload)


class ProcessSafeRememberingObserver(Observer):
    def __init__(self):
        super(ProcessSafeRememberingObserver, self).__init__()
        self.calls = []
        self.q = Queue()
        self.worker = Thread(target=self.worker)
        self.worker.start()

    def notify(self, event):
        self.q.put(event)

    def kill(self):
        self.q.put(None)
        self.worker.join()

    def worker(self):
        while True:
            event = self.q.get()
            if event:
                self.calls.append(event.payload)
            else:
                return


if __name__ == '__main__':
    observable = Observable()
    observer = Observer()

    observable.register_observer(observer)

    observable.notify_observers()

