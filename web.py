import bottle
import graph_tool.all as gt
import json

# 100% totally unscalable web interface.
# It's noddy, but it works.

g = gt.load_graph("graph_pool.xml.gz")

def vtx_to_json(vtx):
    return {
        'type': 'vertex',
        'id': g.vertex_index[vtx],
        'name': g.vertex_properties['system_name'][vtx],
        'x': g.vertex_properties['system_x'][vtx],
        'y': g.vertex_properties['system_y'][vtx],
        'z': g.vertex_properties['system_z'][vtx]
    }

def edge_to_json(edge):
    return {
        'type': 'edge',
        'jump_distance': g.edge_properties['jump_distance'][edge]
    }

@bottle.route('/')
def index():
    return bottle.static_file('index.html', root='templates/',
            mimetype='text/html')


@bottle.route('/api/system')
def find_systems():
    q = bottle.request.query.q
    max_ret = bottle.request.query.max
    
    if not max_ret or max_ret > 10:
        max_ret = 10

    i = 0
    ret = []
    for v in g.vertices():
        if len(q) < 1 or q.lower() in str(g.vertex_properties['system_name'][v]).lower():
            ret.append(vtx_to_json(v))
            i = i + 1
        
        if i >= max_ret:
            break

    return json.dumps(ret)

@bottle.route('/api/system/<id:re:\d+>')
def find_system_by_id(id):
    system = g.vertex(id)
    if not system:
        bottle.abort(404, "No such system.")
    
    return vtx_to_json(system)

@bottle.route('/api/system/<name>')
def find_system_by_name(name):
    systems = gt.find_vertex(g, g.vertex_properties['system_name'], name)
    if len(systems) < 1:
        bottle.abort(404, "No such system.")
    
    return vtx_to_json(systems[0])

@bottle.route('/api/path/<origin_id:re:\d+>/<destination_id:re:\d+>/<max_jump_distance:re:\d+>')
def find_path(origin_id, destination_id, max_jump_distance):
    origin = g.vertex(origin_id)
    destination = g.vertex(destination_id)
    if not origin or not destination:
        bottle.abort(400, "Origin or destination unknown")

    v = gt.GraphView(
        g, 
        efilt=lambda e: (g.edge_properties['jump_distance'][e]) <= float(max_jump_distance)
    ) 
    vlist,elist = gt.shortest_path(v, origin, destination)

    ret = []

    if len(vlist) > 0:
        for vtx, edge in zip(vlist, elist):
            ret.append(vtx_to_json(vtx))
            ret.append(edge_to_json(edge))
        ret.append(vtx_to_json(vlist[-1]))

    return json.dumps(ret)

bottle.run(host='localhost', port=3000)
