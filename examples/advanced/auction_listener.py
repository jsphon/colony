from colony.graphs.auction_listener import AuctionListener

WIDGET_AUCTIONS = {'red': {'status': 'OPEN'},
                   'green': {'status': 'OPEN'},
                   'blue': {'status': 'CLOSED'}}

AUCTION_PRICES = {'red': {'status': 'OPEN', 'price': 10},
                  'green': {'status': 'OPEN', 'price': 20},
                  'blue': {'status': 'CLOSED', 'price': 30}}


def get_auctions(category):
    if category == 'widgets':
        return WIDGET_AUCTIONS
    elif category == 'dongles':
        return {'round': {'status': 'OPEN'}}


def get_prices(auction_catalogue=None):
    results = {}
    for auction_id in auction_catalogue:
        results[auction_id] = AUCTION_PRICES[auction_id]
    return results


def save_prices(prices, auction_catalogue=None):
    for k, v in prices.items():
        print('Saving prices for %s: %s' % (str(k), str(v)))

    # Return the input. This is a bit smelly.
    return prices


if __name__ == '__main__':
    graph = AuctionListener(get_auctions, get_prices, save_prices)
    graph.start()

    # Update the auctions
    graph.get_auctions_node.notify('widgets')
    print('active auctions %s' % graph.active_auctions_node.get_value())

    # Update the prices
    graph.get_prices_node.notify()
    # Active auctions node should only have 2 elements
    print('active auctions %s' % graph.active_auctions_node.get_value())

    from colony.visualiser import display_colony_graph

    display_colony_graph(graph)
