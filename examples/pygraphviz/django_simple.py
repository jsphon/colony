import pygraphviz as pgv

from colony.visualiser import display_graph

if __name__ == '__main__':

    A = pgv.AGraph()  # init empty graph
    # set some default node attributes
    A.node_attr['style'] = 'filled'
    A.node_attr['shape'] = 'circle'
    # Add edges (and nodes)
    A.add_edge(1, 2)
    A.add_edge(2, 3)
    A.add_edge(1, 3)
    A.layout()  # layout with default (neato)

    display_graph(A)