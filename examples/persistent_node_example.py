from colony.node import PersistentNode


def get_data(seed):
    import datetime
    s = datetime.datetime.utcnow().strftime('%Y-%b-%d %H:%M:%S')
    return {'hello': '%s %s' % (seed, s)}


if __name__ == '__main__':

    persistent_node = PersistentNode(target_func=get_data, name='example')

    print('Persistent node value initialised at %s' % persistent_node.get_value())

    persistent_node.notify(0)

    print('Persistent Node Ended at %s' % persistent_node.get_value())

    recovered_node = PersistentNode(target_func=get_data, name='example')

    print('Recovered Node has value at %s' % recovered_node.get_value())
