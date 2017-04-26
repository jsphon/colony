import os
import tempfile

from colony.node import Graph, DictionaryNode


class AuctionListener(Graph):

    def __init__(self, get_auctions_args=None,
                 get_prices_args=None,
                 save_prices_args=None,
                 save_prices_kwargs=None,
                 get_auctions_kwargs=None,
                 get_prices_kwargs=None,
                 ):
        super(AuctionListener, self).__init__()

        if not isinstance(get_auctions_args, (list, tuple)):
            get_auctions_args = (get_auctions_args, ) if get_auctions_args else tuple()

        if not isinstance(get_prices_args, (list, tuple)):
            get_prices_args = (get_prices_args, ) if get_prices_args else tuple()

        if not isinstance(save_prices_args, (list, tuple)):
            save_prices_args = (save_prices_args, ) if save_prices_args else tuple()

        get_auctions_kwargs = get_auctions_kwargs or {}
        self.get_auctions_node = self.add_node(*get_auctions_args, **get_auctions_kwargs)
        self.update_node = self.add_node(update,
                                         node_args=(self.get_auctions_node,))

        name = os.path.basename(tempfile.NamedTemporaryFile().name)
        self.active_auctions_node = self.add(DictionaryNode,
                                             node_args=(self.update_node,),
                                             name=name)

        self.auction_keys_node = self.add_node(to_dict_keys, node_kwargs={'d':self.active_auctions_node})

        get_prices_kwargs = get_prices_kwargs or {}
        #get_prices_kwargs['node_kwargs'] = {'auction_catalogue': self.active_auctions_node}
        get_prices_kwargs['node_args'] = (self.auction_keys_node, )
        self.get_prices_node = self.add_thread_node(*get_prices_args, **get_prices_kwargs)

        save_prices_kwargs = save_prices_kwargs or {}
        save_prices_kwargs['node_args'] = (self.get_prices_node,)
        save_prices_kwargs['node_kwargs'] = {'auction_catalogue': self.active_auctions_node}

        self.save_prices_node = self.add_thread_node(*save_prices_args, **save_prices_kwargs)
        self.close_filter_node = self.add_node(close_filter,
                                               node_args=(self.save_prices_node,))

        self.delete_node = self.add_node(delete,
                                         node_args=(self.close_filter_node,))

        self.delete_node.output_port.register_observer(self.active_auctions_node.reactive_input_ports[0])


def to_dict_keys(d=None):
    d = d or {}
    return list(d.keys())


def update(data):
    return 'update', data


def delete(data):
    return 'delete', tuple(data.keys())


def close_filter(prices):
    result = {}
    if prices:
        for k, v in prices.items():
            if v['status'] == 'CLOSED':
                result[k] = v
    return result
