
import ipdb
import datetime

import time

weekdayDict = {0:"Monday" , 1:"Tuesday" , 2:"Wednesday" , 3:"Thursday" , 4:"Friday" , \
        5: "Saturday" , 6:"Sunday"}

import mechanize

from bs4 import BeautifulSoup

import requests

import re


class megatrain:


    """set up names of form, control ids etc """

    FORM_NAME = "ctl01"
    CONTROL_STATE_ID = "JourneyPlanner$ddlLeavingFromState"
    LEAVING_FROM_CONTROL_ID = "JourneyPlanner$ddlLeavingFrom"
    TRAVELLING_TO_CONTROL_ID = "JourneyPlanner$ddlTravellingTo"
    NUM_PASSENGERS_CONTROL_ID = "JourneyPlanner$txtNumberOfPassengers"

    PATH = "http://uk.megabus.com/"


    def __init__(self):

        """use mechanize to open webpage.
        code originally from 
        http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet
        """
        self._br = mechanize.Browser()
        self._br.set_handle_robots(False)
        self._br.set_handle_refresh(False)
        self._br.addheaders = [('User-agent', 'Firefox')]

        self._webpage = self._br.open(megatrain.PATH)

        self.set_input(megatrain.NUM_PASSENGERS_CONTROL_ID, "1")

        __ = self._br.submit()

        self.city_dict = self.create_city_dict()



    """ if field is text field, control.type will be "text"
    if is dropdown select box, will be "select"
    if latter, input is required to be of list type
    """


    def set_input(self, controlid, input):

        self._br.select_form(megatrain.FORM_NAME) 

        control = self._br.form.find_control(controlid)
        control.readonly = False
        control.disabled = False
        if control.type == "text":
            control.value = input

        elif control.type == "select":
            control.value = [input]

        else:
            raise ValueError("Control is of unknown type : %s " % control.type)

        return control


    def create_city_dict(self):

        city_dict = {}

        self._br.select_form(megatrain.FORM_NAME) 

        """ just select cities in England (1), Scotland (2) or Wales (3) """

        for country_id in range (1,4):

            leaving_from_state_control = self._br.form.find_control(megatrain.CONTROL_STATE_ID)
            leaving_from_state_control.value = [str(country_id)]

            response = self._br.submit()
        
            self._br.select_form(megatrain.FORM_NAME) 
        
            leaving_from_control = self._br.form.find_control(megatrain.LEAVING_FROM_CONTROL_ID)
            
            for item in leaving_from_control.items:
                if int(item.name) > 0:
                    city_dict[item.attrs["label"]] = item.name
        
        return city_dict

    def refresh_page(self):
        __ = self._br.open(megatrain.PATH)

    def train_routes_from_city(br, path, city_dict, leaving_from_city):

        train_route_list = []

        print "checking leaving from : " , leaving_from_city

        set_input(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")
        set_input(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])

        response = br.submit()

        """ iterate through the travelling to cities in the dropdown that results from 
        submitting each of the leaving from cities
        """

        """TODO change below to function but make input blank"""
       
        br.select_form(FORMNAME) 
        travelling_to_control = br.form.find_control(TRAVELLINGTOCONTROLID)
        travelling_to_control.readonly = False
        travelling_to_control.disabled = False

        """ create list from travelling to dropdown that only includes cities in mainland GB
        """

        travelling_to_city_list = ( [travelling_to_city_tag.attrs['label'] 
                for travelling_to_city_tag in travelling_to_control.items 
                if travelling_to_city_tag.attrs['label'] in city_dict] )


        for travelling_to_city in travelling_to_city_list:

            print "travelling to : ", travelling_to_city

            webpage = br.open(path)
            set_input(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")
            set_input(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
            response = br.submit()

            """ above needed to be done in order to refresh the travelling to dropdown before
            submitting the same info but this time with travelling to filled in as well
            was getting incorrect responses before clearing the form with the above, even
            though it looks redundant
            """

            set_input(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
            set_input(br, FORMNAME, TRAVELLINGTOCONTROLID, city_dict[travelling_to_city])

            response = br.submit()
            br.select_form(FORMNAME)
            travelling_by_control = br.form.find_control("JourneyPlanner$ddlTravellingBy")

            for travelling_by_item in travelling_by_control.items:
                if travelling_by_item.name == "2":  # train
                    print "TRAIN ON ROUTE %s to %s " % (leaving_from_city , travelling_to_city)
                    train_route_list.append([leaving_from_city , travelling_to_city])

        return train_route_list


    def getSchedule(leaving_from_city, travelling_to_city, days_to_check = 8):

        resulturlstart = "http://uk.megabus.com/JourneyResults.aspx?originCode=%s&destinationCode=\
                %s&passengerCount=1&transportType=2&outboundDepartureDate=" % \
                (city_dict[leaving_from_city] , city_dict[travelling_to_city])

        now = datetime.date.today()

        """ format of datestring is 24%2f03%2f2016 for 24th march 2016"""
        dateformat = "%d%%2f%m%%2f%Y" 

        timere = re.compile("\\d\\d:\\d\\d")

        schedulelist = []

        """trains are added to the booking screen from 36 days. so start checking from 28 days
        and keep checking for 7 days to cover a week. In future possibly will check for 
        2 weeks, so start from 22 days in case a partic week just has that train booked up
        already"""

        for i in range(36 - days_to_check ,36):

            day = now + datetime.timedelta(i)

            """strftime %w uses clearly incorrect ;) 0 as Sunday"""

            weekday = int(day.strftime("%w")) - 1

            datestring = day.strftime(dateformat)

            resulturlstring = resulturlstart + datestring

            webpage_text = requests.get(resulturlstring).text

            soup = BeautifulSoup(webpage_text)

            row_tag_list = soup.find_all(id=\
                    re.compile("JourneyResylts_OutboundList_GridViewResults_ctl\d\d_row_item"))

            for row_tag in row_tag_list:
                two_tag = row_tag.find(class_="two")

                timelist = timere.findall(str(two_tag))

                schedule = megaroute.MegaSchedule(weekday , \
                        time.strptime(timelist[0], "%H:%M"), \
                        time.strptime(timelist[1], "%H:%M"))

                schedulelist.append(schedule)

        return schedulelist
                


          


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





