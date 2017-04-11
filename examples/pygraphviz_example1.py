import pygraphviz as pgv

from colony.visualiser import display_graph

if __name__ == '__main__':
    a = pgv.AGraph()

    a.add_edge(1, 2)
    a.add_edge(2, 3)
    a.add_edge(1, 3)

    display_graph(a)
