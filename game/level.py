class Level:
    def __init__(self, total_time):
        self.complete = False
        self.death = False 
        self.total_time = total_time
        self.good_deeds = 0

    def get_time(self): return self.total_time

    def set_time(self, time): self.total_time = time

    def get_coins(self): raise NotImplementedError

    def set_coins(self, coins): raise NotImplementedError

    def get_good_deeds(self): return self.good_deeds

