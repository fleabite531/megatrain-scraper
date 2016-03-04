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

"""
FORMNAME = "ctl01"
CONTROLSTATEID = "JourneyPlanner$ddlLeavingFromState"
LEAVINGFROMCONTROLID = "JourneyPlanner$ddlLeavingFrom"
TRAVELLINGTOCONTROLID = "JourneyPlanner$ddlTravellingTo"
NUMPASSENGERSCONTROLID = "JourneyPlanner$txtNumberOfPassengers"

PATH = "http://uk.megabus.com/"

"""


def main():


    """ get path either as file or url and open contents into webpage_text as string"""

    parser = argparse.ArgumentParser()

    """made below into constant as doesn't really change"""
    # parser.add_argument("path", help="path to file or url to process")

    parser.add_argument("output", help="output file")
    parser.add_argument("--from-city", "-f", help="optional field if only want to check leaving "
            "from a specific city")

    parser.add_argument("--print-valid-cities", "-p", help="Print a list of valid city names "
            "and exit", action="store_true", default=False)

    parser.add_argument("--get-schedule", help="Get schedule as well as route list",
            action="store_true", default=False)

    args = parser.parse_args()

    """
    br = mechanize.Browser()
    # br.set_all_readonly(False)    # allow everything to be written to
    br.set_handle_robots(False)   # ignore robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Firefox')]

    webpage = br.open(args.path)
    """

    """ set number of passengers as 1 """

    # set_input(br, FORMNAME, NUMPASSENGERSCONTROLID, "1")

    # response = br.submit()


    """create dictionary for all the cities from the leaving from cities"""

    # city_dict = create_city_dict(br)


    mega_session = megaroute.megatrain()

    """ if valid_cities argument, then just print valid cities and exit"""

    if args.print_valid_cities:
        print "Valid cities are : "
        for city in sorted(mega_session.city_dict.keys()):
            print city
        sys.exit()


    train_route_list = []

    """ reopen page in order to clear country field as its optional but defines leaving_from"""

    # webpage = br.open(args.path)

    mega_session.refresh_page()

    ipdb.set_trace()


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

