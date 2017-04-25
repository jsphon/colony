import multiprocessing
from multiprocessing import Process

from colony.node import AsyncWorker
from colony.node import Node


class ExampleTargetClass(object):
    def __init__(self, c):
        print('Initialising ExampleTargetClass')
        self.data = set([c])
        print('data is %s' % str(self.data))

    def execute(self, x):
        print('%s received %s' % (self.name, x))
        self.data.add(x)
        return self.data

    @property
    def name(self):
        return multiprocessing.current_process().name


if __name__ == '__main__':
    n = Node(target_class=ExampleTargetClass,
             target_class_args=(0,),
             node_worker_class=AsyncWorker,
             node_worker_class_args=(Process,),
             node_worker_class_kwargs={'num_threads': 5},
             )
    n.start()

    for i in range(100):
        n.notify(i)

    # Wait for the worker to empty its work queue
    n.worker.join()

    # Notice how the results aren't deterministic, as each worker will
    # have a different state
    print(n.get_value())
