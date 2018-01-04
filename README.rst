.. image:: https://travis-ci.org/bast/ascii2graph.svg?branch=master
   :target: https://travis-ci.org/bast/ascii2graph/builds
.. image:: https://img.shields.io/badge/license-%20MPL--v2.0-blue.svg
   :target: ../master/LICENSE


ascii2graph
===========

Converts ASCII text to a graph (represented as a dictionary).


Installation
------------

::

  $ pip install ascii2graph


Example
-------

.. code-block:: python

  from ascii2graph import graph

  text = r'''
  a--boo
  |   |   x
  |   |  /
  c---d-e
      | |
      f-g'''

  result = graph(text)
  print(result)

This produces the following graph (dictionary):

.. code-block:: python

  result = {(1, 4, 'a'): [(4, 4, 'c'), (1, 7, 'boo')],
            (4, 4, 'c'): [(1, 4, 'a'), (4, 8, 'd')],
            (4, 8, 'd'): [(4, 4, 'c'), (4, 10, 'e'), (1, 7, 'boo'), (6, 8, 'f')],
            (4, 10, 'e'): [(2, 12, 'x'), (4, 8, 'd'), (6, 10, 'g')],
            (2, 12, 'x'): [(4, 10, 'e')],
            (6, 8, 'f'): [(6, 10, 'g'), (4, 8, 'd')],
            (6, 10, 'g'): [(6, 8, 'f'), (4, 10, 'e')],
            (1, 7, 'boo'): [(4, 8, 'd'), (1, 4, 'a')]}

Nodes can be anything that is not one of these characters::

  -
  |
  /
  \


Suggestions? Corrections? Pull requests?
----------------------------------------

Yes please!
