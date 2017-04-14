import os
import tempfile
from subprocess import call

import pygraphviz as pgv

from colony.node import AsyncNode


def display_colony_graph(g, layout='dot'):
    A = pgv.AGraph(directed=True)

    for n in g.nodes:
        src = n._target_func.__name__

        for e in n.output_port.observers:
            if e in e.node.reactive_input_ports:
                color = 'red'
            elif e in e.node.passive_input_ports.values():
                color = 'gray'
            else:
                print('e not recognised')

            if isinstance(e.node, AsyncNode):
                style = 'dashed'
            else:
                style = 'solid'
            tgt = e.node._target_func.__name__
            A.add_edge(src, tgt, color=color, style=style)

    display_graph(A, layout=layout)


def display_graph(g, layout='dot'):
    """ Display the graph locally
        Currently only works on Ubuntu
    """

    basename = '%s.png' % tempfile.TemporaryFile().name
    path = os.path.join(tempfile.tempdir, basename)
    gg = g.copy()
    gg.layout(layout)
    gg.draw(path)

    call(['xdg-open', path])


if __name__ == '__main__':
    A = pgv.AGraph()

    A.add_edge(1, 2)
    A.add_edge(2, 3)
    A.add_edge(1, 3)
    display_graph(A)

    A = pgv.AGraph()

    A.add_edge('one', 'two', color='red', label='1-2', style='dashed')
    A.add_edge('two', 'three')
    A.add_edge('one', 'three')
    display_graph(A)
