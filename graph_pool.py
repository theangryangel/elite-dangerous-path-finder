import json
import numpy
import multiprocessing
from graph_tool.all import *
from functools import partial

raw = open('response.json')
data = json.load(raw)
raw.close()

g = Graph(directed=False)
g.vertex_properties['system_name'] = g.new_vertex_property('string')
g.vertex_properties['system_x'] = g.new_vertex_property('double')
g.vertex_properties['system_y'] = g.new_vertex_property('double')
g.vertex_properties['system_z'] = g.new_vertex_property('double')
g.edge_properties['jump_distance'] = g.new_edge_property("double")

print "Adding systems..."

for system in data['d']['systems']:
    print " %s @ %d,%d,%d with confidence %d" % ( 
        system['name'], 
        system['coord'][0],
        system['coord'][1], system['coord'][2],
        system['cr']
    )

    v = g.add_vertex()
    g.vertex_properties['system_name'][v] = system['name'].encode('ASCII', 'ignore')
    g.vertex_properties['system_x'][v] = system['coord'][0]
    g.vertex_properties['system_y'][v] = system['coord'][1]
    g.vertex_properties['system_z'][v] = system['coord'][2]

# Dumping everything back into a cache and referencing vertexes via
# vertex_index seems, at least on my system, to be
# faster than interrogating the graph directly, and also quicker than
# pre-calculating everything and then find find_vertex using prop name to create
# edges.
cache = []

for v in g.vertices():
    cache.append({
        'vertex_index': int(g.vertex_index[v]),
        'system_x': float(g.vertex_properties['system_x'][v]),
        'system_y': float(g.vertex_properties['system_y'][v]),
        'system_z': float(g.vertex_properties['system_z'][v]),
    })

# Known issues
# - this does not take into account objects that are "in the way"
def find_valid_jumps(destination, origin):
    a = numpy.array((
        origin['system_x'], 
        origin['system_y'],
        origin['system_z'] 
    ))

    b = numpy.array((
        destination['system_x'],
        destination['system_y'],
        destination['system_z'] 
    ))

    total_dist = numpy.sqrt(numpy.sum((a-b)**2))

    # max jump distance from http://elite-dangerous.wikia.com/wiki/Ships
    if total_dist <= 19.56 and total_dist > 0:
        return { 'origin': origin['vertex_index'], 'destination':
                destination['vertex_index'], 'jump_distance': total_dist }


process_count = multiprocessing.cpu_count() * 2 + 1

# It may be possible to parallelize this further by having a process pool for
# the systems. However, for simplicity this works at an acceptable speed.
# By simply parallelizing like this, it takes the job (when single process) from
# 5+ hours on my core i7 laptop to <30 minutes.
print "Calculating valid jumps..."

for system in cache:
    pool = multiprocessing.Pool(processes=process_count)
    partial_find_valid_jumps = partial(find_valid_jumps, origin=system)
    res = pool.map(partial_find_valid_jumps, cache)
    pool.close()
    pool.join()
    res = filter(None, res)

    print 'Origin system %s %d valid jumps' % (
        g.vertex_properties['system_name'][g.vertex(system['vertex_index'])],
        len(res)
    )
        
    for edge in res:
        j = g.add_edge(edge['origin'], edge['destination'])
        g.edge_properties['jump_distance'][j] = edge['jump_distance']


print "Removing parallel edges..."
remove_parallel_edges(g)

print "Removing loops..."
remove_self_loops(g)

print "Saving..."
g.save("graph_pool.xml.gz")

print "Job's done!"
