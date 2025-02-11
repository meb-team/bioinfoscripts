#!/usr/bin/env python3
""" This script aims to generate ICS file from a list of dates
Note, like primarly all events are planned from 8:00 to 12:00, the accepted
format is a list of dates in the format YYYY-MM-DD 

This will (maybe) improved in the future
"""

from argparse import RawTextHelpFormatter
from datetime import datetime, timedelta

import sys
import argparse
import icalendar as ic

UID = 0

def _add_reminder(date, n_day_before = 1):
    """Create a reminder 1 day BEFORE the date passed in argument
    If the reminder is a saturday or a sunday, it is set to the friday.
    'date' is a tuple of datetime.datetime() objects
    """
    global UID
    # Set the reminder "n_day_before"
    reminder_start = date[0] - timedelta(days = n_day_before)
    reminder_end = reminder_start + timedelta(hours = 1) # A 1 hour event for the reminder

    # Is it during the week-end? 6 = saturday; 7 = sunday
    if datetime.isoweekday(reminder_start) >= 6:
        for i in range(1,7):
            # print(date[0], "reminder test, week day = ",
            #     datetime.isoweekday(date[0] - timedelta(days = i)))

            if datetime.isoweekday(date[0] - timedelta(days = i)) == 5:
                reminder_start = date[0] - timedelta(days = i)
                reminder_end = reminder_start + timedelta(hours = 1    )
                break

    event = ic.Event()
    event.add('summary', 'Préparer sortie terrain')
    event.add('description', "Charger batterie et sondes; Préparer materiel")
    event.add('dtstart', reminder_start)
    event.add('dtend', reminder_end)
    event.add('dtstamp', datetime.today())
    event.add('uid', str(UID))
    UID += 1

    return event


def parse_dates(infile):
    """Read the file with all dates, Input format : YYYY-MM-DD
    Return a list of tuples [(start, end)]
    """
    all_dates = []
    # loop over the lines of line (dates)
    with open(infile, "r", encoding="utf-8") as fi:
        for line in fi.readlines():
            start = datetime.strptime(line.rstrip() + "-8", "%Y-%m-%d-%H")  # Force the 8 am
            end = datetime.strptime(line.rstrip() + "-12", "%Y-%m-%d-%H")  # Force noon

            # store as tuple
            all_dates.append((start, end))

    return all_dates


def create_events(cal, dates):
    """Add events to a calendar
    Dates are stored are as list of tuple (start, end)
    Futur improvment : leave the choice of events name"""
    global UID

    for date in dates:
        # create the event
        event = ic.Event()
        event.add('summary', 'Sortie ANR Diamond')
        event.add('description', "Prélèvement sur le lac d'Aydat")
        event.add('dtstart', date[0])
        event.add('dtend', date[1])
        event.add('dtstamp', datetime.today())
        event.add('uid', str(UID))
        UID += 1

        # Add the event in the calendar
        cal.add_component(event)

        # Add a reminder for the current event
        reminder = _add_reminder(date)
        cal.add_component(reminder)
    return cal


def print_cal(cal, outfile):
    """Print the calendar in a file"""

    with open(outfile, 'wb') as f:
        f.write(cal.to_ical())
    return True


if __name__ == "__main__":
    __description__ = "This is a very basic program that generates ICal file " \
                      "for a single event (8am - 12am)\nplus creates reminder " \
                      "the day before, in the form of a one-hour event (8 - 9am)."
    parser = argparse.ArgumentParser(formatter_class = RawTextHelpFormatter,
                                     description = __description__)
    parser.add_argument('dates', help='File with the dates, format "YYYY-MM-DD"')
    parser.add_argument('ouftile', help='Basename of the file that contains the'
                        ' calendar')

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        ## Add checks if input and output file exists ==> raise error

        # init the calendar
        cal = ic.Calendar()

        # Add mandatory fields to be compliant with the RFC 5545 3.6
        cal.add('prodid', 'DIAMOND ANR calendar')
        cal.add('version', '2.0')

        # Read the dates
        dates = parse_dates(args.dates)

        # Create the events 
        ## Create an event 48h before to charge the batteries
        ## and book the material
        cal = create_events(cal, dates)

        # write the ICS file
        print_cal(cal, args.ouftile + ".ics")

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
