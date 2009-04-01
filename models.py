import math
from util import intersect

class Point:
	def __init__(self, name, x, y):
		self.name = name
		self.x = x
		self.y = y

	def distance_to(self, p):
		dx = self.x - p.x
		dy = self.y - p.y

		return math.sqrt(dx**2 + dy**2)

	def __eq__(self, p):
		return self.x == p.x and self.y == p.y

	def __ne__(self, p):
		return not self.__eq__(p)

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		return (self.x, self.y).__hash__()

class Road:
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def length(self):
		return self.start.distance_to(self.end)

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
		times = []

		for region in regions:
			for i, road in enumerate(self.roads):
				intersection = intersect(road, region)
				if intersection != None:
					time = sum([road.length() for road in self.roads[:i]]) / speed
					time += road.start.distance_to(Point(None, intersection[0], intersection[1])) / speed
					times.append(time)
					break

		return times

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
