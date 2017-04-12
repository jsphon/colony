import os
import tempfile

from colony.node import Graph, DictionaryNode


class AuctionListener(Graph):

    def __init__(self, get_auctions, get_prices, save_prices):
        super(AuctionListener, self).__init__()

        self.get_auctions_node = self.add_node(get_auctions)
        self.update_node = self.add_node(update,
                                         node_args=(self.get_auctions_node,))

        name = os.path.basename(tempfile.NamedTemporaryFile().name)
        self.active_auctions_node = self.add(DictionaryNode,
                                             node_args=(self.update_node,),
                                             name=name)

        self.get_prices_node = self.add_node(get_prices,
                                             node_kwargs={'auction_catalogue': self.active_auctions_node})

        self.save_prices_node = self.add_node(save_prices,
                                              node_args=(self.get_prices_node,),
                                              node_kwargs={'auction_catalogue': self.active_auctions_node})

        self.close_filter_node = self.add_node(close_filter,
                                               node_args=(self.save_prices_node,))

        self.delete_node = self.add_node(delete,
                                         node_args=(self.close_filter_node,))

        self.delete_node.output_port.register_observer(self.active_auctions_node.reactive_input_ports[0])


def update(data):
    return 'update', data


def delete(data):
    return 'delete', tuple(data.keys())


def close_filter(prices):
    result = {}
    for k, v in prices.items():
        if v['status'] == 'CLOSED':
            result[k] = v
    return result
