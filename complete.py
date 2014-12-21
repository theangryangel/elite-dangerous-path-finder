from graph_tool.all import *

max_jump_distance = 15

print 'Loading graph'
g = load_graph("graph_pool.xml.gz")

print 'Drawing PDF'
graphviz_draw(g, 
    output="complete.pdf"
)
