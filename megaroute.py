
import ipdb
import datetime

import time

weekdayDict = {0:"Monday" , 1:"Tuesday" , 2:"Wednesday" , 3:"Thursday" , 4:"Friday" , \
        5: "Saturday" , 6:"Sunday"}


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

          


"""departure and arrivaltimes should be datetime.time objects
day should be an int 0-6, 0 being Monday, 6 being Sunday
"""

class MegaSchedule:

    def __init__(self, day, departuretime, arrivaltime, duration=0, carrier="", schedule=[]):
        self._departuretime = departuretime
        self._arrivaltime = arrivaltime
        self._day = day

    def __repr__(self):
        return "%s : %s - %s" % (weekdayDict[self._day], \
                time.strftime("%H:%M", self._departuretime) , \
                time.strftime("%H:%M", self._arrivaltime))


    def __eq__(self, other):
        return other._departuretime==self._departuretime and \
                other._arrivaltime == self._arrivaltime and \
                other._day == self._day

    def __lt__(self, other):
        if self._day != other._day:
            return self._day < other._day

        if self._arrivaltime != other._arrivaltime:
            return self._arrivaltime < other._arrivaltime

        return self._departuretime < other._departuretime

    def __gt__(self, other):
        if self._day != other._day:
            return self._day > other._day

        if self._departuretime != other._departuretime:
            return self._departuretime > other._departuretime

        return self._arrivaltime > other._arrivaltime


    def returnSchedule(self):
        return self._day, self._departuretime, self._arrivaltime

          


class MegaRoute:
    def __init__(self, fromcity, tocity, schedule=None, departuretime=None, arrivaltime=None, days = []):
        self._fromcity = fromcity
        self._tocity = tocity
        self._schedule = []
        if departuretime:
            self._schedule.append(MegaSchedule(departuretime, arrivaltime, days))

        if schedule:
            self._schedule.append(schedule)

    def isRoute(self, fromcity, tocity):

        if self._fromcity == fromcity and self._tocity == tocity:
            return True

        return False

    def __repr__(self):
        return_string = "[%s -> %s]" % (self._fromcity, self._tocity)

        if not len(self._schedule):
            return_string += ": "
            return_string += ", ".join([schedule for schedule in self._schedule])

        return return_string

    def isSchedule(self, departuretime, arrivaltime):
        for schedule in self._schedule:
            print ""


    def addSchedule(self, departuretime, arrivaltime, days=[]):
        self._schedule.append(MegaSchedule(departuretime, arrivaltime, days))

    def addSchedule(self, schedule):
        self._schedule.append(schedule)
        

    def returnScheduleList(self):
        return self._schedule

    def returnRoute(self):
        return self._fromcity, self._tocity, self._schedule

    def __iter__(self):
        return iter(self._schedule)
    



class MegaRouteList:
    def __init__(self):
        self._route_list = []

    def AddRoute(self, fromcity, tocity):
        self._route_list.append(MegaRoute(fromcity, tocity))

    def ViewRoute(self, fromcity, tocity):
        for index in range(0, len(self._route_list)):
            # if self.route_list[index][0] == fromcity and self.route_list[index][1] == tocity:
            if self._route_list[index].IsRoute(fromcity, tocity):
                return self._route_list[index]
        
        return None
    

    def __getitem__(self, key):
        return self._route_list[key]



    def __iter__(self):
        return iter(self._route_list)

    def __len__(self):
        return len(self._route_list)

    def __repr__(self):
        return '.'.join([str(route) for route in self._route_list])




    def AddRouteSchedule(self, fromcity, tocity, day, time):
        """check if route already exists in list, else add it"""

        need_to_add = True

        for index in range(0, len(self._route_list)):
            if self._route_list[index][0] == fromcity and self._route_list[index][1] == tocity:
                need_to_add = False
                break

        if need_to_add:
            self.AddRoute(fromcity, tocity)





