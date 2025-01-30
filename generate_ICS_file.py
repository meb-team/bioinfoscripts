#!/usr/bin/env python3
""" This script aims to generate ICS file from a list of dates
Note, like primarly all events are planned from 8:00 to 12:00, the accepted
format is a list of dates in the format YYYY-MM-DD 

This will (maybe) improved in the future
"""

from argparse import RawTextHelpFormatter
from datetime import datetime

import os
import sys
import argparse
import icalendar as ic


def parse_dates():
    """Read the file with all dates, return a list
    Input format : YYYY-MM-DD"""
    all_dates = []
    # loop over the lines of line (dates)
    # start = datetime.strptime(line + "-8", "%Y-%m-%d-%H")  # Froce the 8 am
    # end = datetime.strptime(line + "-12", "%Y-%m-%d-%H")  # Froce the 12 am
    # Store both values as a tuple in a list

    return all_dates


def print_cal(cal, outfile):
    """Print the calendar in a file"""

    with open(outfile, 'wb') as f:
        f.write(cal.to_ical())
    return True


def create_events(cal, dates):
    """Add events to a calendar, based on the dates provided
    Futur improvment : leave the choice of events name"""

    # A for loop to go through all dates; one event per date

    # event = ic.Event()
    # event.add('summary', 'Sortie ANR Diamond')
    # event.add('description', "Prélèvement sur le lac d'Aydat")
    # event.add('dtstart', datetime(2025, 1, 31, 8, 0, 0))
    # event.add('dtend', datetime(2025, 1, 31, 13, 0, 0))

    # # Add the event in the calendar
    # cal.add_component(event)

    return cal

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class = RawTextHelpFormatter)
    parser.add_argument('dates', help='File with the dates, format "YYYY-MM-DD"')

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        # init the calendar
        cal = ic.Calendar()

        # Read the dates

        # Create the events
        ## Create an event 48h before to charge the batteries
        ## and book the material

        # write the ICS file

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
