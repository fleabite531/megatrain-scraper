"""
Finds all routes on megabus booking page for which a train option is available

Uses mechanize module in order to emulate a browser

Megabus website requires 
each previous input to be completed, and then uses POST to retrieve options for next 
control. Mandatory controls are in this order: 
Number of passesngers > Leaving from > Travelling to > Travelling by.
For each stage in the control all the previous controls need to be reset

Program opens page.
Builds dictionary of all megabus destinations and their assigned megabus integer id.
Itereates through this dictionary
For each entry this is set as leaving from option
A list is created of all destinations in travelling to control. This is different for 
each leaving from destination and so is created anew for each leaving from.
This travelling to list is then iterated through. If the travelling by now includes
train, the leaving from - travelling to combination is saved into a list of paired lists

"""

"""
TODO :
fix so doesn't require output file if printing list of cities
add schedule flag to acquire schedule

"""

import megaroute

import sys
import argparse
import ipdb
import datetime

import time

import mechanize

from bs4 import BeautifulSoup

import requests

import re

"""set up names of form, control ids etc """

FORMNAME = "ctl01"
CONTROLSTATEID = "JourneyPlanner$ddlLeavingFromState"
LEAVINGFROMCONTROLID = "JourneyPlanner$ddlLeavingFrom"
TRAVELLINGTOCONTROLID = "JourneyPlanner$ddlTravellingTo"
NUMPASSENGERSCONTROLID = "JourneyPlanner$txtNumberOfPassengers"


"""TODO combine 2 below into single function"""

def set_text_field(br, formname, controlid, input):

    br.select_form(formname) 

    control = br.form.find_control(controlid)
    control.readonly = False
    control.disabled = False
    control.value = input

    return control

def set_dropdown_control(br, formname, controlid, input):

    br.select_form(formname) 

    control = br.form.find_control(controlid)
    control.readonly = False
    control.disabled = False
    control.value = [input]

    return control


def create_city_dict(br):

    city_dict = {}

    br.select_form(FORMNAME) 

    """ just select cities in England (1), Scotland (2) or Wales (3) """

    for country_id in range (1,4):

        leaving_from_state_control = br.form.find_control(CONTROLSTATEID)
        leaving_from_state_control.value = [str(country_id)]

        response = br.submit()
    
        br.select_form(FORMNAME) 
    
        leaving_from_control = br.form.find_control(LEAVINGFROMCONTROLID)
        
        for item in leaving_from_control.items:
            if int(item.name) > 0:
                city_dict[item.attrs["label"]] = item.name
    
    return city_dict


def train_routes_from_city(br, path, city_dict, leaving_from_city):

    train_route_list = []

    print "checking leaving from : " , leaving_from_city

    set_text_field(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")
    set_dropdown_control(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
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
        set_text_field(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")
        set_dropdown_control(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
        response = br.submit()

        """ above needed to be done in order to refresh the travelling to dropdown before
        submitting the same info but this time with travelling to filled in as well
        was getting incorrect responses before clearing the form with the above, even
        though it looks redundant
        """

        set_dropdown_control(br, FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
        set_dropdown_control(br, FORMNAME, TRAVELLINGTOCONTROLID, city_dict[travelling_to_city])

        response = br.submit()
        br.select_form(FORMNAME)
        travelling_by_control = br.form.find_control("JourneyPlanner$ddlTravellingBy")

        """TODO just do an if ... in ... """
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
            

def main():


    """ get path either as file or url and open contents into webpage_text as string"""

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to file or url to process")
    parser.add_argument("output", help="output file")
    parser.add_argument("--from-city", "-f", help="optional field if only want to check leaving "
            "from a specific city")

    parser.add_argument("--print-valid-cities", "-p", help="Print a list of valid city names "
            "and exit", action="store_true", default=False)

    parser.add_argument("--get-schedule", help="Get schedule as well as route list",
            action="store_true", default=False)

    args = parser.parse_args()

    """use mechanize to open webpage.
    code originally from 
    http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet
    """

    br = mechanize.Browser()
    # br.set_all_readonly(False)    # allow everything to be written to
    br.set_handle_robots(False)   # ignore robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Firefox')]

    webpage = br.open(args.path)

    """ set number of passengers as 1 """

    set_text_field(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")

    response = br.submit()


    """create dictionary for all the cities from the leaving from cities"""

    city_dict = create_city_dict(br)

    """ if valid_cities argument, then just print valid cities and exit"""

    if args.print_valid_cities:
        print "Valid cities are : "
        for city in sorted(city_dict.keys()):
            print city
        sys.exit()


    train_route_list = []

    """ reopen page in order to clear country field as its optional but defines leaving_from"""

    webpage = br.open(args.path)


    """if from defined, then set that as city, check if from is valid, else exit
    else iterate through whole list 
    """

    if args.from_city is None:
        for leaving_from_city in city_dict:
            train_route_list += train_routes_from_city(br, args.path, city_dict, leaving_from_city)

    else:

        from_city = ""
        for city in city_dict:
            if city.lower() == args.from_city.lower():
                from_city = city
                break

        if from_city == "":
            sys.exit("Error %s not valid city. Use --print-cities option to see list of \
                    city options." % (args.from_city))
       
        print "Checking for trains leaving from " + from_city

        train_routes = megaroute.MegaRouteList()

        train_route_list = train_routes_from_city(br, args.path, city_dict, from_city)

        for fromcity, tocity in train_route_list:
            train_routes.AddRoute(fromcity, tocity)

        for route in train_routes:
            print "Train route : " , route

        ipdb.set_trace()

        """pre making MegaTrain class
        train_route_list = train_routes_from_city(br, city_dict, from_city)
        """

    if args.get_schedule:
        for route in train_routes:
            ipdb.set_trace()
            from_city, to_city = route.returnRoute()
            schedulelist = getSchedule(from_city, to_city)


    for city_pairs in train_route_list:
        print "Train available leaving from %s travelling to %s" % (city_pairs[0],city_pairs[1])

    with open(args.output, "w+") as f:
        f.write("Megatrains available on following routes " + str(datetime.date.today()))
        for city_pairs in train_route_list:
            f.write("FROM : " + city_pairs[0] + " TO : " + city_pairs[1] + "\n")



if __name__ == "__main__":
    main()

