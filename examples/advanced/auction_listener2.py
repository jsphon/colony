from colony.graphs.auction_listener import AuctionListener

if __name__ == '__main__':

    graph = AuctionListener()
    graph.start()

    # Update the auctions
    graph.get_auctions_node.notify('donkeys')
    print('active auctions %s' % graph.active_auctions_node.get_value())

    # Update the prices
    graph.get_prices_node.notify()
    # Active auctions node should only have 2 elements
    print('active auctions %s' % graph.active_auctions_node.get_value())

