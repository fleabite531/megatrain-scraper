
import ipdb


class MegaRoutes:
    def __init__(self):
        self.route_list = []

    def AddRoute(self, fromcity, tocity):
        self.route_list.append([fromcity, tocity])

    def __iter__(self):
        return iter(self.route_list)


