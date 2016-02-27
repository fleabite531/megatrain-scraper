
import ipdb
import datetime

import time


"""departure and arrivaltimes should be datetime.time objects"""
class OLDMegaSchedule:

    def __init__(self, departuretime, arrivaltime, days,  duration=0, carrier="", schedule=[]):
        self.departuretime = departuretime
        self.arrivaltime = arrivaltime
        self.days = [days]

    def __repr__(self):
        return_string = "%s - %s : " % (self.departuretime , self.arrivaltime)
        return_string += ', '.join([day for day in self.days])

        return return_string

    def isSchedule(self, departuretime, arrivaltime):
        return departuretime==self.departuretime and \
                arrivaltime == self.arrivaltime

    def whichDays(self):
        return self.days


    def addDay(self, day):
        if not day in self.days:
            self.days.append(day)
            return True

        return False

    def returnSchedule(self):
        return self.departuretime, self.arrivaltime, self.days

          


"""departure and arrivaltimes should be datetime.time objects"""
class MegaSchedule:

    def __init__(self, day, departuretime, arrivaltime, duration=0, carrier="", schedule=[]):
        self.departuretime = departuretime
        self.arrivaltime = arrivaltime
        self.day = day

    def __repr__(self):
        ipdb.set_trace()
        return "%s : %s - %s" % (self.day, \
                self.departuretime.strftime("%H:%M") , self.arrivaltime)


    def __eq__(self, other):
        return other.departuretime==self.departuretime and \
                other.arrivaltime == self.arrivaltime and \
                other.day == self.day

    def __lt__(self, other):
        if self.day != other.day:
            return self.day < other.day

        if self.arrivaltime != other.arrivaltime:
            return self.arrivaltime < other.arrivaltime

        return self.departuretime < other.departuretime




    def returnSchedule(self):
        return self.day, self.departuretime, self.arrivaltime

          


class MegaRoute:
    def __init__(self, fromcity, tocity, departuretime=None, arrivaltime=None, days = []):
        self.fromcity = fromcity
        self.tocity = tocity
        self.schedule = []
        if departuretime:
            self.schedule.append(MegaSchedule(departuretime, arrivaltime, days))

    def isRoute(self, fromcity, tocity):

        if self.fromcity == fromcity and self.tocity == tocity:
            return True

        return False

    def __repr__(self):
        return_string = "[%s -> %s]" % (self.fromcity, self.tocity)

        if not len(self.schedule):
            return_string += ": "
            return_string += ", ".join([schedule for schedule in self.schedule])

        return return_string

    def isSchedule(self, departuretime, arrivaltime):
        for schedule in self.schedule:
            print ""


    def addSchedule(self, departuretime, arrivaltime, days=[]):

        
        self.schedule.append(MegaSchedule(departuretime, arrivaltime, days))
        

    def returnScheduleList(self):
        return self.schedule

    def returnRoute(self):
        return self.fromcity, self.tocity, self.schedule

    def __iter__(self):
        return iter(self.schedule)
    



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





