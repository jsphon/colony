import os
import tempfile
from colony.node import Graph, DictionaryNode


def get_auctions(category):
    if category == 'donkeys':
        return {0:{'status':'OPEN'},
                1: {'status': 'OPEN'},
                2: {'status': 'CLOSED'}}
    elif category == 'mules':
        return [3, 4, 5]


def update(data):
    return 'update', data


def delete(data):
    return 'delete', tuple(data.keys())


def get_prices(auction_ids=None):
    results = {}
    for auction_id in auction_ids:
        if auction_id==2:
            results[auction_id] = {'status': 'CLOSED', 'price': 123}
        else:
            results[auction_id] = {'status': 'OPEN', 'price': 123}
    return results


def save_prices(prices):

    for k, v in prices.items():
        print('Saving prices for %s: %s'%(str(k), str(v)))

    # Return the input. This is a bit smelly.
    return prices


def close_filter(prices):
    result = {}
    for k, v in prices.items():
        print(k, v)
        if v['status'] == 'CLOSED':
            result[k] = v
    return result


if __name__ == '__main__':
    graph = Graph()

    get_auctions_node = graph.add_node(get_auctions)

    update_node = graph.add_node(update, node_args=(get_auctions_node, ))

    name = os.path.basename(tempfile.NamedTemporaryFile().name)
    active_auctions_node = graph.add(DictionaryNode, node_args=(update_node, ), name=name)

    get_prices_node = graph.add_node(get_prices, node_kwargs={'auction_ids': active_auctions_node})
    save_prices_node = graph.add_node(save_prices, node_args=(get_prices_node, ))
    close_filter_node = graph.add_node(close_filter, node_args=(save_prices_node,))
    delete_node = graph.add_node(delete, node_args=(close_filter_node,))

    delete_node.output_port.register_observer(active_auctions_node.reactive_input_ports[0])

    graph.start()

    get_auctions_node.notify('donkeys')

    print('active auctions %s' % active_auctions_node.get_value())
    get_prices_node.notify()

    print('prices %s' % get_prices_node.get_value())
    print('close_filter %s' % close_filter_node.get_value())
    print('active auctions %s' % active_auctions_node.get_value())