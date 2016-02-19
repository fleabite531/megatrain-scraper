# Finds all routes on megabus booking page for which a train option is available
#
# Uses mechanize module in order to emulate a browser
#
# Megabus website requires 
# each previous input to be completed, and then uses POST to retrieve options for next 
# control. Mandatory controls are in this order: 
# Number of passesngers > Leaving from > Travelling to > Travelling by.
# For each stage in the control all the previous controls need to be reset
#
# Program opens page.
# Builds dictionary of all megabus destinations and their assigned megabus integer id.
# Itereates through this dictionary
# For each entry this is set as leaving from option
# A list is created of all destinations in travelling to control. This is different for 
# each leaving from destination and so is created anew for each leaving from.
# This travelling to list is then iterated through. If the travelling by now includes
# train, the leaving from - travelling to combination is saved into a list of paired lists
# 


import sys
import argparse
import ipdb
import datetime

import mechanize

from bs4 import BeautifulSoup

# set up names of form, control ids etc

FORMNAME = "ctl01"
CONTROLSTATEID = "JourneyPlanner$ddlLeavingFromState"
LEAVINGFROMCONTROLID = "JourneyPlanner$ddlLeavingFrom"
TRAVELLINGTOCONTROLID = "JourneyPlanner$ddlTravellingTo"
NUMPASSENGERSCONTROLID = "JourneyPlanner$txtNumberOfPassengers"





def set_text_field(formname, controlid, input):

    br.select_form(formname) 

    control = br.form.find_control(controlid)
    control.readonly = False
    control.disabled = False
    control.value = input

    return control

def set_dropdown_control(formname, controlid, input):

    br.select_form(formname) 

    control = br.form.find_control(controlid)
    control.readonly = False
    control.disabled = False
    control.value = [input]

    return control




def create_city_dict(br):


    city_dict = {}

    br.select_form(FORMNAME) 

    # just select cities in England (1), Scotland (2) or Wales (3)

    for country_id in range (1,4):

        leaving_from_state_control = br.form.find_control(CONTROLSTATEID)
        leaving_from_state_control.value = [str(country_id)]

        response = br.submit()
    
        br.select_form(FORMNAME) 
    
        leaving_from_control = br.form.find_control(LEAVINGFROMCONTROLID)
        
        for item in leaving_from_control.items:
            if int(item.name) > 0:
                # below changed 18/2 keyvalueswap
                city_dict[item.attrs["label"]] = item.name
                # city_dict[int(item.name)] = item.attrs["label"]
    

    return city_dict





def train_routes_from_city(br, city_dict, leaving_from_city):

    train_route_list = []


    # below changed 18/2 keyvalueswap
    print "checking leaving from : " , leaving_from_city
    # print "checking leaving from : " , city_dict[leaving_from_city]


    set_text_field(FORMNAME, NUMPASSENGERSCONTROLID, "1")

    # below changed 18/2 keyvalueswap
    set_dropdown_control(FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
    # set_dropdown_control(FORMNAME, LEAVINGFROMCONTROLID, str(leaving_from_city))


    response = br.submit()

    # iterate through the travelling to cities in the dropdown that results from 
    # submitting each of the leaving from cities

    br.select_form(FORMNAME) 
    travelling_to_control = br.form.find_control(TRAVELLINGTOCONTROLID)
    travelling_to_control.readonly = False
    travelling_to_control.disabled = False

    # create list from travelling to dropdown that only includes cities in mainland GB

    # below changed 18/2 keyvalueswap

    travelling_to_city_list = [travelling_to_city_tag.attrs['label'] for travelling_to_city_tag \
            in travelling_to_control.items if travelling_to_city_tag.attrs['label'] in city_dict]

    """
    travelling_to_city_list = [int(travelling_to_city_tag.name) for travelling_to_city_tag \
            in travelling_to_control.items if int(travelling_to_city_tag.name) in city_dict]
    """



    for travelling_to_city in travelling_to_city_list:


        # below changed 18/2 keyvalueswap
        print "travelling to : ", travelling_to_city
        # print "travelling to : ", city_dict[int(travelling_to_city)]

        webpage = br.open(args.path)
        set_text_field(FORMNAME, NUMPASSENGERSCONTROLID, "1")

        # below changed 18/2 keyvalueswap
        set_dropdown_control(FORMNAME, LEAVINGFROMCONTROLID, city_dict[leaving_from_city])
        # set_dropdown_control(FORMNAME, LEAVINGFROMCONTROLID, str(leaving_from_city))


        response = br.submit()

        # above needed to be done in order to refresh the travelling to dropdown before
        # submitting the same info but this time with travelling to filled in as well
        # was getting incorrect responses before clearing the form with the above, even
        # though it looks redundant

        br.select_form(FORMNAME)
        leaving_from_control = br.form.find_control(LEAVINGFROMCONTROLID)
        leaving_from_control.readonly = False
        leaving_from_control.disabled = False
        # below changed 18/2 keyvalueswap
        leaving_from_control.value = [str(city_dict[leaving_from_city])]
        # leaving_from_control.value = [str(leaving_from_city)]
        travelling_to_control = br.form.find_control(TRAVELLINGTOCONTROLID)
        travelling_to_control.readonly = False
        travelling_to_control.disabled = False

        # below changed 18/2 keyvalueswap
        leaving_from_control.value = [str(city_dict[leaving_from_city])]
        #leaving_from_control.value = [str(leaving_from_city)]

        # below changed 18/2 keyvalueswap
        travelling_to_control.value = [str(city_dict[travelling_to_city])]
        #travelling_to_control.value = [str(travelling_to_city)]

        response = br.submit()
        br.select_form(FORMNAME)
        travelling_by_control = br.form.find_control("JourneyPlanner$ddlTravellingBy")
        for travelling_by_item in travelling_by_control.items:
            if travelling_by_item.name == "2":  # train
                # below changed 18/2 keyvalueswap
                print "TRAIN ON ROUTE %s to %s " % (leaving_from_city , travelling_to_city)
                # print "TRAIN ON ROUTE %s to %s " % (city_dict[leaving_from_city] , city_dict[travelling_to_city])

                # below changed 18/2 keyvalueswap
                train_route_list.append([leaving_from_city , travelling_to_city])
                # train_route_list.append([city_dict[leaving_from_city] , city_dict[travelling_to_city]])




    return train_route_list








# MAIN starts here

# get path either as file or url and open contents into webpage_text as string

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to file or url to process")
parser.add_argument("output", help="output file")
parser.add_argument("--from-city", help="optional field if only want to check leaving from a specific\
        city")
args = parser.parse_args()




# use mechanize to open webpage.
# code originally from http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet

br = mechanize.Browser()
# br.set_all_readonly(False)    # allow everything to be written to
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Firefox')]

webpage = br.open(args.path)

# set number of passengers as 1

set_text_field(FORMNAME, NUMPASSENGERSCONTROLID, "1")



response = br.submit()


"""create dictionary for all the cities from the leaving from cities"""



city_dict = create_city_dict(br)


train_route_list = []

""" reopen page in order to clear country field as its optional but defines leaving_from"""

webpage = br.open(args.path)

"""if from defined, then set that as city, check if from is valid, else exit
else iterate through whole list 
"""



if args.from_city is None:
    for leaving_from_city in city_dict:
        train_route_list += train_routes_from_city(br, city_dict, leaving_from_city)

else:
    print "Checking for trains leaving from " + args.from_city

    if args.from_city not in city_dict:
        print "Error %s not valid city." % (args.from_city)
        exit()
   
    train_route_list = train_routes_from_city(br, city_dict, args.from_city)







for city_pairs in train_route_list:
    print "Train available leaving from %s travelling to %s" % (city_pairs[0],city_pairs[1])



with open(args.output, "w+") as f:
    f.write("Megatrains available on following routes " + str(datetime.date.today()))
    for city_pairs in train_route_list:
        f.write("FROM : " + city_pairs[0] + " TO : " + city_pairs[1] + "\n")


exit()
    


