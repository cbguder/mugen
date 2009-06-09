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
