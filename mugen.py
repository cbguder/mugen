#!/usr/bin/env python

SIMULATION_TIME = 60.0

# Average vehicle speed in m/s
SPEED_MEAN  = 30.0
SPEED_STDEV = 4.0

# Vehicle density in vehicles/hour
VEHICLE_DENSITY = 2600
ARRIVAL_MEAN    = VEHICLE_DENSITY / 3600.0
ARRIVAL_STDEV   = 0.8

import sys
import random
from parser import parse
from models import Point, Path

def main():
	if len(sys.argv) < 2:
		print "Usage: mugen.py FILE"
		sys.exit()

	filename = sys.argv[1]

	f = open(filename)
	vehicles = generate(f)
	f.close()

def generate(f):
	(points, roads) = parse(f)

	paths = find_all_paths(points, roads)

	longest_dist = 0.0
	for path in paths:
		dist = path.total_distance()
		if dist > longest_dist:
			longest_dist = dist

	trim = longest_dist / SPEED_MEAN
	t = 0.0

	vehicles = []

	while t < SIMULATION_TIME + trim:
		speed   = random.gauss(SPEED_MEAN, SPEED_STDEV)
		arrival = t + random.gauss(ARRIVAL_MEAN, ARRIVAL_STDEV)
		path    = random.choice(paths)

		vehicles.append({'speed': speed, 'arrival': arrival, 'path': path})

		t = arrival

#	plot_vehicle_count(vehicles, trim)
	generate_ns2_scene(vehicles, trim)

	return vehicles

def generate_ns2_scene(vehicles, trim = 0.0):
#	$node_(0) set X_ 726.589600
#	$node_(0) set Y_ 732.986267
#	$node_(0) set Z_ 0.000000
#	$ns_ at 0.000000 "$node_(0) setdest 549.615173 549.615173 32.812519"

	i = 0
	for v in vehicles:
		rel_times  = v['path'].get_times(v['speed'])
		real_times = [t + v['arrival'] for t in rel_times]
		sim_times  = [t - trim for t in real_times]
		num_times  = len(sim_times)

		# If the vehicle leaves the area before the simulation starts
		if sim_times[-1] < 0:
			continue

		j = 0

		while j < num_times and sim_times[j] < 0:
			j += 1

		if j == 0:
			initial = v['path'][0]
		else:
			# Interpolate position at trim
			ratio = sim_times[j] / (sim_times[j] - sim_times[j-1])
			initial = interpolate(v['path'][j], v['path'][j-1], ratio)

			j -= 1
			if sim_times[j] < 0:
				sim_times[j] = 0.0

		if sim_times[j] < SIMULATION_TIME:
			print "$node_(%d) set X_ %f" % (i, initial.x)
			print "$node_(%d) set Y_ %f" % (i, initial.y)
			print "$node_(%d) set Z_ %f" % (i, 0)

			print '$ns_ at %f "$beacon_(%d) PeriodicBroadcast ON"' % (sim_times[j], i)

		while j < num_times - 1:
			t = sim_times[j]

			if t < SIMULATION_TIME:
				p = v['path'][j+1]
				print '$ns_ at %f "$node_(%d) setdest %f %f %f"' % (t, i, p.x, p.y, v['speed'])

			j += 1

		if sim_times[-1] < SIMULATION_TIME:
			params = (sim_times[-1], i, i)
			print '$ns_ at %f "$ns_ detach-agent $node_(%d) $agent_(%d)"'  % params
			print '$ns_ at %f "$ns_ detach-agent $node_(%d) $beacon_(%d)"'  % params

		i += 1

def interpolate(a, b, ratio):
	dx = b.x - a.x
	dy = b.y - a.y

	x = a.x + ratio * dx
	y = a.y + ratio * dy

	return Point(None, x, y)

def plot_vehicle_count(vehicles, trim = 0.0):
	v_count = {0.0: 0}

	for v in vehicles:
		v_count[v['arrival']] = 1
		dt = v['path'].total_distance() / v['speed']
		v_count[v['arrival'] + dt] = -1

	times = sorted(v_count.keys())

	real_count = 0
	print "set style data lines"
	print "set xrange[%f:%f]" % (trim, trim + SIMULATION_TIME)
	print "set yrange[0:]"
	print "plot '-' t 'Vehicles'"
	print "0.0 0"
	for t in times:
		real_count += v_count[t]
		print "%f %d" % (t, real_count)

def find_all_paths(points, roads):
	paths  = []
	tpaths = []

	entrances = points[:]
	exits     = points[:]

	for road in roads:
		if road.end in entrances:
			entrances.remove(road.end)
		if road.start in exits:
			exits.remove(road.start)

	for road in roads:
		if road.start in entrances:
			tpaths.append(Path([road.start, road.end]))

	while len(tpaths):
		t2paths = []
		for path in tpaths:
			if len(path) > 1 and path[0] in entrances and path[-1] in exits:
				paths.append(path)
			elif not path.is_cyclic():
				for road in roads:
					if road.start == path[-1]:
						t2paths.append(Path(path.points + [road.end]))
		tpaths = t2paths

	return paths

if __name__ == '__main__':
	main()
