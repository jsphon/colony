from multiprocessing import Process, Queue
from threading import Thread

from colony.node import Colony, AsyncNode, NodeEvent
from colony.observer import Observer


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


def _x_squared(x):
    return x*x


if __name__ == '__main__':

    obs = ProcessSafeRememberingObserver()
    col = Colony()

    node = col.add(AsyncNode, target=_x_squared, async_class=Process)
    node.output_port.register_observer(obs)

    col.start()

    node.input_port.notify(NodeEvent(1))
    node.input_port.notify(NodeEvent(2))
    node.input_port.notify(NodeEvent(3))

    col.kill()
    obs.kill()

    print(obs.calls)
