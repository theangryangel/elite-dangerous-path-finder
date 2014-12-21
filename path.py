from graph_tool.all import *

max_jump_distance = 15

print 'Loading graph...'
g = load_graph("graph_pool.xml.gz")

print 'Finding vertex...'
origin = find_vertex(g, g.vertex_properties['system_name'], "Sol")[0]

destination = find_vertex(g, g.vertex_properties['system_name'], "HIP 20019")[0]

print origin
print destination

print 'Filtering graph with max_jump_distance <= %f...' % max_jump_distance
# Filtered graph view
v = GraphView(g, efilt=lambda e: g.edge_properties['jump_distance'][e] <= max_jump_distance )

print 'Finding shortest path...'
vlist,elist = shortest_path(v, destination, origin)

print 'Generating GraphView for pdf...'
pdf = GraphView(v, vfilt=lambda v: v in vlist )

print 'Drawing PDF'
graph_draw(pdf, 
    output_size=(2048,2048),
    output="path.pdf",
    vertex_text=g.vertex_properties['system_name'],
    edge_text=g.edge_properties['jump_distance'],
    overlap=False
)

print 'Jump list: '
for vtx, edge in zip(vlist, elist):
    print ' %s' % pdf.vertex_properties['system_name'][vtx]
    print '  jumping %2f ' % pdf.edge_properties['jump_distance'][edge]
print ' %s' % pdf.vertex_properties['system_name'][vlist[-1]]

print 'Job\'s Done!'
