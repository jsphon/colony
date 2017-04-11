import pygraphviz as pgv

from colony.visualiser import display_graph

if __name__ == '__main__':
    A = pgv.AGraph()

    A.add_edge(1, 2)
    A.add_edge(2, 3)
    A.add_edge(1, 3)

    display_graph(A)