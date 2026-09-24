from pygame.time import get_ticks

class Timer:
	def __init__(self, duration, func = None, repeat = False):
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.active = False
		self.repeat = repeat
		self.value = 0

	def activate(self):
		self.active = True
		self.start_time = get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		if self.repeat:
			self.activate()

	def update(self):
		current_time = get_ticks()
		self.value = current_time - self.start_time
		
		if self.value >= self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.value = self.duration # stop value at max
			self.deactivate()

