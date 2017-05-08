from colony.graphs.auction_listener import AuctionListener

WIDGET_AUCTIONS = {'red': {'status': 'OPEN'},
                   'green': {'status': 'OPEN'},
                   'blue': {'status': 'CLOSED'}}

AUCTION_PRICES = {'red': {'status': 'OPEN', 'price': 10},
                  'green': {'status': 'OPEN', 'price': 20},
                  'blue': {'status': 'CLOSED', 'price': 30}}

c = 0


def get_auctions():
    return WIDGET_AUCTIONS


def get_prices(auction_catalogue):
    global c
    c += 1
    results = {}
    print('Getting prices for %s' % str(auction_catalogue))
    for auction_id in auction_catalogue:
        results[auction_id] = AUCTION_PRICES[auction_id].copy()
        results[auction_id]['id'] = c
    return results


def save_prices(prices):#, auction_catalogue=None):
    for k, v in prices.items():
        print('Saving prices for %s: %s' % (str(k), str(v)))

    # Return the input. This is a bit smelly.
    return prices


def on_close(prices, auction_catalogue=None):

    for k, v in prices.items():
        print('Archiving prices for %s: %s' % (str(k), str(v)))

    return prices


if __name__ == '__main__':
    graph = AuctionListener(get_auctions, get_prices, save_prices, on_close, batch_size=1)#, folder)
    graph.start()

    # Update the auctions
    graph.get_latest_auctions()
    print('active auctions %s' % graph.active_auctions_node.get_value())

    # Update the prices
    graph.get_latest_prices()

    print('active auctions %s' % graph.active_auctions_node.get_value())

    from colony.visualiser import display_colony_graph

    display_colony_graph(graph, 'fdp')
    display_colony_graph(graph, 'dot')
