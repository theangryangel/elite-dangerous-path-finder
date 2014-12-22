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

print "Calculating valid jumps..."
def iterate_systems(system, cache):
    partial_find_valid_jumps = partial(find_valid_jumps, origin=system)
    res = map(partial_find_valid_jumps, cache)
    res = filter(None, res)

    print ' %d has %d valid jumps' % (system['vertex_index'], len(res))

    return res

# We split out the system -> all systems distance calculation across multiple
# processes to speed up the calculation.
# Previously I split the distance calc and did 1 system at once. 
# Instead we split the origin systems and do all distance calcs for that one at
# once. 
# This changes the job from 30-45min run for 50ly max jump to <= 16mins on my
# 2013 mbp.
# execnet for future expansion.
pool = multiprocessing.Pool(processes=process_count)
partial_iterate_systems = partial(iterate_systems, cache=cache)
res = pool.map(partial_iterate_systems, cache)
pool.close()
pool.join()
res = filter(None, res)

# Theres probably a better way of doing this.
print 'Adding edges...'
for edge_collection in res:
    for edge in edge_collection:
        print ' %d -> %d @ %d' % (edge['origin'],
                edge['destination'], edge['jump_distance'])
        j = g.add_edge(edge['origin'], edge['destination'])
        g.edge_properties['jump_distance'][j] = edge['jump_distance']

print "Removing parallel edges..."
remove_parallel_edges(g)

print "Removing loops..."
remove_self_loops(g)

print "Saving..."
g.save("graph_pool2.xml.gz")

print "Job's done!"
