# Interactive map displaying nodes and edges
Place to host a file for my bokeh project

The data in the associated .csv file is a sanitized version of the data I'm working with. It consists of 5300 nodes in 1300 groups, and it has over 880,000 edges.

The main thing I want my python code to do is, when I hover over a node, I want line segments to appear between that node and every other node that's in the same group; this I was able to do by repurposing the code in the example at this URL: https://docs.bokeh.org/en/2.4.3/docs/user_guide/interaction/callbacks.html#customjs-for-hover-tool

With a lot of help (I'm not really a programmer), I've accomplished that, plus:

-You can select a node and all of the edges will remain visible, plus all nodes that are not in the same group change color to be less visible
-There's a MiniMap that shows you where you are on the graph
-There's a DataTable that lists all of the nodes and their different groups
  -The DataTable and the graph are interactive: if you click a line on the DataTable, it's equivalent to clicking that node on the graph, and vice versa
