import pygraphviz as pgv

from colony.visualiser import display_graph


if __name__ == '__main__':
    A = pgv.AGraph()

    # set some default node attributes
    A.node_attr['style'] = 'filled'
    A.node_attr['shape'] = 'circle'
    A.node_attr['fixedsize'] = 'true'
    A.node_attr['fontcolor'] = '#FFFFFF'

    # make a star in shades of red
    for i in range(16):
        A.add_edge(0, i)
        n = A.get_node(i)
        n.attr['fillcolor'] = "#%2x0000" % (i * 16)
        n.attr['height'] = "%s" % (i / 16.0 + 0.5)
        n.attr['width'] = "%s" % (i / 16.0 + 0.5)

    # print(A.string())  # print to screen
    # A.write("star.dot")  # write to simple.dot
    # print("Wrote star.dot")
    # A.draw('star.png', prog="circo")  # draw to png using circo
    # print("Wrote star.png")
    display_graph(A, 'circo')