
import ipdb

class MegaRoute:
    def __init__(self, fromcity, tocity, day = "", time = ""):
        self.fromcity = fromcity
        self.tocity = tocity
        self.schedule = []

    def IsRoute(self, fromcity, tocity):
        if self.fromcity == fromcity and self.tocity == tocity:
            return True

        return False

    def __repr__(self):
        return "[%s -> %s]" % (self.fromcity, self.tocity)




class MegaRouteList:
    def __init__(self):
        self.route_list = []

    def AddRoute(self, fromcity, tocity):
        self.route_list.append(MegaRoute(fromcity, tocity))

    def ViewRoute(self, fromcity, tocity):
        for index in range(0, len(self.route_list)):
            # if self.route_list[index][0] == fromcity and self.route_list[index][1] == tocity:
            if self.route_list[index].IsRoute(fromcity, tocity):
                return self.route_list[index]
        
        return None
    


    def __iter__(self):
        return iter(self.route_list)

    def __len__(self):
        return len(self.route_list)

    def __repr__(self):
        return '.'.join([str(route) for route in self.route_list])




    def AddRouteSchedule(self, fromcity, tocity, day, time):
        """check if route already exists in list, else add it"""

        need_to_add = True

        for index in range(0, len(self.route_list)):
            if self.route_list[index][0] == fromcity and self.route_list[index][1] == tocity:
                need_to_add = False
                break

        if need_to_add:
            self.AddRoute(fromcity, tocity)





