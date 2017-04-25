from multiprocessing import Process

from colony.node import AsyncWorker
from colony.node import PersistentNode
from colony.utils.random_name import random_name


def get_data():
    return 'data'


if __name__ == '__main__':
    name = random_name()
    persistent_node = PersistentNode(target_func=get_data,
                                     name=name,
                                     node_worker_class=AsyncWorker,
                                     node_worker_class_args=(Process,),
                                     )

    persistent_node.start()

    print('Persistent node value initialised with %s' % persistent_node.get_value())

    persistent_node.notify()
    persistent_node.worker.join()

    print('Persistent Node Ended at %s' % persistent_node.get_value())

    recovered_node = PersistentNode(target_func=get_data, name=name)

    print('Recovered Node has value %s' % recovered_node.get_value())

    assert recovered_node.get_value() == 'data'
