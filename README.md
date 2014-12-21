# Elite Dangerous Path Finder
Elite Dangerous Path Finder. Maybe incomplete. May have wrong data. Totally
janky proof of concept code.

Takes the output from [Elite Dangerous Star Coordinator](http://edstarcoordinator.com/), 
and calculates feasible jumps between all systems (see TODOs for caveats), and
dumps them into a [graph-tool](http://graph-tool.skewed.de/) graph.

This is not yet a full product. If you can't program, go and use one of the
many, many other tools that does this.

I am not a python-ista/pythonite/whatever, so the quality of the code is
shocking. I know. I don't care.

## TODOs
  - Form into a complete product
  - Speed up importer - maybe using execnet for multiple machine calculation
  - Check if jump occlusion matters in the game
  - Check if calculated jumps are actually correct in the game

## Installing
  - git clone
  - Install requirements `pip install -r requirements.txt`. If you're on a mac
	I'd suggest brew for graph-tool, for simplicity.

### Fetching completely fresh data
I've included my own pre-calculated data. If for some reason you want to
alter/update/edit, then follow the below.

Be aware this can take 30+ minutes, depending on the spec of your machine. It is
not yet possible to distribute this to multiple machines.

  - `python fetch.py` to get a list of stars from
	[Elite Dangerous Star Coordinator](http://edstarcoordinator.com/). Be
	kind. Don't do this too often. response.json contains a cached response.
  - `python graph_pool.py` to rebuild graph_pool.xml.gz. This will contain a
	precalculated graph of stars and feasible jumps. This currently assumes
	several things and needs to be investigated as to whether or not things like
	jumps with systems in the way need to be removed.
	It pre-calculates all possible jumps using multiple python processes. On my
	Core i7 late 2013 Macbook Pro this takes around 30 minutes. As more features
	are added this will take longer. 

### Interogating the data
  - `python path.py` to find the shortest path from any 2 given points. No
	arguments for now, just edit the file.

### Drawing a path of all systems and jumps
  - `python complete.py && open complete.pdf` 
