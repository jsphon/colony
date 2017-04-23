import os
import tempfile

from colony.node import DictionaryNode


if __name__ == '__main__':

    name = os.path.basename(tempfile.NamedTemporaryFile().name)

    dictionary_node = DictionaryNode(name=name)
    dictionary_node.start()
    print('Dictionary node value initialised at %s' % dictionary_node.get_value())

    dictionary_node.notify(('update', {'hello':'world'}))

    print('dictionary node has value %s' % dictionary_node.get_value())
