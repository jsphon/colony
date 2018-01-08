from colony.node import Graph, DictionaryNode, BatchArgInputPort


class AuctionListener(Graph):

    def __init__(self, get_auctions_args=None,
                 get_prices_args=None,
                 save_prices_args=None,
                 on_close_args=None,
                 save_prices_kwargs=None,
                 get_auctions_kwargs=None,
                 get_prices_kwargs=None,
                 close_filter=None,
                 on_close_kwargs=None,
                 batch_size=5,
                 filename=None,
                 folder=None,
                 name=None,
                 logger=None
                 ):
        super(AuctionListener, self).__init__(name=name, logger=logger)

        if not isinstance(get_auctions_args, (list, tuple)):
            get_auctions_args = (get_auctions_args, ) if get_auctions_args else tuple()

        if not isinstance(get_prices_args, (list, tuple)):
            get_prices_args = (get_prices_args, ) if get_prices_args else tuple()

        if not isinstance(save_prices_args, (list, tuple)):
            save_prices_args = (save_prices_args, ) if save_prices_args else tuple()

        if not isinstance(on_close_args, (list, tuple)):
            on_close_args = (on_close_args, ) if on_close_args else tuple()

        get_auctions_kwargs = get_auctions_kwargs or {}
        self.get_auctions_node = self.add_node(*get_auctions_args, **get_auctions_kwargs)
        self.update_node = self.add_node(update,
                                         node_args=(self.get_auctions_node,))

        self.active_auctions_node = self.add(DictionaryNode,
                                             node_args=(self.update_node,),
                                             name=filename,
                                             folder=folder)

        self.auction_keys_node = self.add_node(to_dict_keys, node_kwargs={'d':self.active_auctions_node})

        get_prices_kwargs = get_prices_kwargs or {}
        get_prices_kwargs['node_args'] = (self.auction_keys_node, )
        get_prices_kwargs['reactive_input_ports'] = BatchArgInputPort(batch_size=batch_size)
        self.get_prices_node = self.add_thread_node(*get_prices_args, **get_prices_kwargs)

        save_prices_kwargs = save_prices_kwargs or {}
        save_prices_kwargs['node_args'] = (self.get_prices_node,)

        self.save_prices_node = self.add_thread_node(*save_prices_args, **save_prices_kwargs)
        close_filter = close_filter or default_close_filter
        self.close_filter_node = self.add_node(close_filter, node_args=(self.save_prices_node,))

        on_close_kwargs = on_close_kwargs or {}
        on_close_kwargs['node_args'] = (self.close_filter_node, )
        on_close_kwargs['node_kwargs'] = {'auction_catalogue':self.active_auctions_node}
        self.on_close_node = self.add_node(*on_close_args, **on_close_kwargs)

        self.delete_node = self.add_node(delete, node_args=(self.on_close_node,))

        self.delete_node.output_port.register_observer(self.active_auctions_node.reactive_input_ports[0])

    def get_latest_auctions(self):
        if self.is_alive:
            self.get_auctions_node.notify()
        else:
            print('Cannot get auctions, is_alive=%s'%self.is_alive)

    def get_latest_prices(self):
        if self.is_alive:
            self.auction_keys_node.notify()
        else:
            print('Cannot get prices, is_alive=%s' % self.is_alive)


def to_dict_keys(d=None):
    d = d or {}
    return list(d.keys())


def update(data):
    return 'update', data


def delete(data):
    return 'delete', tuple(data.keys())


def default_close_filter(prices):
    result = {}
    if prices:
        for k, v in prices.items():
            if v['status'] == 'CLOSED':
                result[k] = v

    return result
