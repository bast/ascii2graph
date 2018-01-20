.. image:: https://travis-ci.org/bast/ascii2graph.svg?branch=master
   :target: https://travis-ci.org/bast/ascii2graph/builds
.. image:: https://img.shields.io/badge/license-%20MPL--v2.0-blue.svg
   :target: ../master/LICENSE


ascii2graph
===========

Converts ASCII text to a graph (represented as a dictionary of connections and
angles). It can represent directed and undirected graphs.


Installation
------------

::

  $ pip install ascii2graph


Example
-------

.. code-block:: python

  from ascii2graph import graph

  text = r'''
  a->boo
  ^   |   x
  |   v  /
  c<--d-e
      | |
      f-g'''

  result = graph(text)
  print(result)

This produces the following graph (dictionary):

.. code-block:: python

  result = {(1, 4, 'a'): [(1, 7, 'boo', 90)],
            (4, 4, 'c'): [(1, 4, 'a', 0)],
            (4, 8, 'd'): [(4, 4, 'c', 270), (4, 10, 'e', 90), (6, 8, 'f', 180)],
            (4, 10, 'e'): [(2, 12, 'x', 45), (4, 8, 'd', 270), (6, 10, 'g', 180)],
            (2, 12, 'x'): [(4, 10, 'e', 225)],
            (6, 8, 'f'): [(6, 10, 'g', 90), (4, 8, 'd', 0)],
            (6, 10, 'g'): [(6, 8, 'f', 270), (4, 10, 'e', 0)],
            (1, 7, 'boo'): [(4, 8, 'd', 180)]}

Nodes can be anything that is not one of these characters::

  - | / \ v ^ < >

There is one exception (sorry!): If "/" is part of `[sometext/foo]`, then it is not interpreted
as an edge. The reason is that I needed this to visualize Git branches and Git history where I needed
`[origin/somebranch]`.


But ... why?
------------

I use it to create SVG graphics for teaching Git DAGs from plain text files
because it is so easy to change a text file and simply generate a new SVG
image. This module helps me to obtain a graph representation that I can use
somewhere else to generate graphics.


Suggestions? Corrections? Pull requests?
----------------------------------------

Yes please!
