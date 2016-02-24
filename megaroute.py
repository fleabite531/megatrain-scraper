
import ipdb


class MegaRoutes:
    def __init__(self):
        self.route_list = []

    def AddRoute(self, fromcity, tocity):
        self.route_list.append([fromcity, tocity])

    def __iter__(self):
        return iter(self.route_list)

    def __len__(self):
        return len(self.route_list)

    def __repr__(self):
        return_string = ""
        for route in self.route_list:
            return_string += str(route)

        return return_string



    def AddRouteSchedule(self, fromcity, tocity, day, time):
        """check if route already exists in list, else add it""
        self.index


