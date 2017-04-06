import os
import tempfile

from colony.node import Graph, DictionaryNode


if __name__ == '__main__':

    graph = Graph()

    name = os.path.basename(tempfile.NamedTemporaryFile().name)
    dictionary_node = graph.add(DictionaryNode, name=name)

    print('Dictionary node value initialised at %s' % dictionary_node.get_value())

    graph.start()

    dictionary_node.notify(('update', {'hello':'world'}))

    print('dictionary node has value %s' % dictionary_node.get_value())
    graph.stop()
