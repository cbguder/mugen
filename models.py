import math

class Point:
	def __init__(self, name, x, y):
		self.name = name
		self.x    = x
		self.y    = y

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
	def __init__(self, a, b):
			self.start = a
			self.end   = b

	def length(self):
		return self.start.distance_to(self.end)

class Path:
	def __init__(self, points = []):
		self.points = points[:]

	def append(self, p):
		self.points.append(p)

	def is_cyclic(self):
		return len(set(self.points)) != len(self.points)

	def total_distance(self):
		distance = 0.0
		for i in range(len(self.points) - 1):
			distance += self.points[i].distance_to(self.points[i+1])
		return distance

	def get_times(self, speed):
		times = []
		t = 0.0

		times.append(t)
		for i in range(len(self.points) - 1):
			t += self.points[i].distance_to(self.points[i+1]) / speed
			times.append(t)

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
