from colony.node import DictionaryNode, Graph, PersistentNode
from colony.visualiser import display_colony_graph
import multiprocessing
import os
#p=multiprocessing.current_process()

import tempfile

name = os.path.basename(tempfile.NamedTemporaryFile().name)
print('name is %s')

def pass_through1(x):
    n = multiprocessing.current_process().name
    print('pass_through1 %s Passing %s through' % (n, str(x)))
    return x

def pass_through2(x):
    n = multiprocessing.current_process().name
    print('pass_through2 %s Passing %s through' % (n, str(x)))
    return x


if __name__ == '__main__':
    graph = Graph()

    process_node1 = graph.add_process_node(pass_through1)
    process_node2 = graph.add_process_node(pass_through2)

    persistent_node = graph.add(DictionaryNode, name=name)
    persistent_node.set_value({})

    process_node1.output_port.register_observer(persistent_node.reactive_input_ports[0])
    process_node2.output_port.register_observer(persistent_node.reactive_input_ports[0])

    graph.start()

    process_node1.notify(('update', {'letter': 'a'}))
    process_node2.notify(('update', {'number': 1}))

    graph.stop()

    print('On main thread, process_node1 has value %s' % process_node1.get_value())
    print('On main thread, persistent node has value %s' % persistent_node.get_value())

    recovered_node = DictionaryNode(name=name)
    print('Recovered Node has value at %s' % recovered_node.get_value())

    #display_colony_graph(graph)

    #
    # def test():
    #     import time
    #     time.sleep(1)
    #     print('hi')
    #
    # worker_1 = multiprocessing.Process(name='worker 1', target=test)
    # worker_2 = multiprocessing.Process(name='worker 1', target=test) # use default name
    #
    # worker_1.start()
    # worker_2.start()