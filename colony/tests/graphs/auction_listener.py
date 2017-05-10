import unittest

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


def get_prices(auction_catalogue):
    results = {}
    print('Getting prices')
    for auction_id in auction_catalogue:
        results[auction_id] = AUCTION_PRICES[auction_id]
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


class MyTestCase(unittest.TestCase):
    def test_get_auctions_notify(self):
        graph = AuctionListener(get_auctions, get_prices, save_prices, on_close)
        graph.start()

        graph.get_auctions_node.notify('widgets')

        graph.stop()

        self.assertEqual(WIDGET_AUCTIONS, graph.get_auctions_node.get_value())

    def test_get_prices_notify(self):
        graph = AuctionListener(get_auctions, get_prices, save_prices, on_close)
        graph.start()

        graph.get_auctions_node.notify('widgets')
        graph.get_prices_node.notify()
        graph.get_latest_prices()

        graph.stop()

        self.assertEqual(AUCTION_PRICES, graph.get_prices_node.get_value())

        import time
        time.sleep(1)

        expected = {'red': {'status': 'OPEN'},
                    'green': {'status': 'OPEN'}}
        print(graph.active_auctions_node.get_value())
        self.assertEqual(expected, graph.active_auctions_node.get_value())


if __name__ == '__main__':
    unittest.main()
