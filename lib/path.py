from point import Point
from road import Road
from util import intersect

class Path:
	def __init__(self, points = []):
		self.points = points[:]
		self.roads = self.get_roads()

	def append(self, p):
		self.points.append(p)

	def is_cyclic(self):
		return len(set(self.points)) != len(self.points)

	def total_distance(self):
		return sum([road.length() for road in self.roads])

	def get_roads(self):
		return [Road(self.points[i], self.points[i+1]) for i in range(len(self.points) - 1)]

	def get_times(self, speed):
		times = []
		t = 0.0

		times.append(t)
		for road in self.roads:
			t += road.length() / speed
			times.append(t)

		return times

	def get_collisions(self, regions, speed):
		collisions = []

		for region in regions:
			for i, road in enumerate(self.roads):
				intersection = intersect(road, region)
				if intersection != None:
					time = sum([road.length() for road in self.roads[:i]]) / speed
					time += road.start.distance_to(Point(None, intersection[0], intersection[1])) / speed
					collision = {'time': time, 'region': region}
					collisions.append(collision)
					break

		return collisions

	def __len__(self):
		return len(self.points)

	def __getitem__(self, key):
		return self.points[key]

	def __setitem__(self, key, value):
		self.points[key] = value

	def __str__(self):
		return self.points.__str__()

	def __repr__(self):
		return self.points.__repr__()
