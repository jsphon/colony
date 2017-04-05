from colony.node import Graph, PersistentNode

def get_data(seed):
    import datetime
    s = datetime.datetime.utcnow().strftime('%Y-%b-%d %H:%M:%S')
    return {'hello': '%s %s' % (seed, s)}


if __name__ == '__main__':

    graph = Graph()

    persistent_node = graph.add(PersistentNode, target=get_data, name='example')

    print('Persistent node value initialised at %s' % persistent_node.get_value())

    graph.start()

    persistent_node.notify(0)

    graph.stop()

    print('Persistent Node Ended at %s' % persistent_node.get_value())
