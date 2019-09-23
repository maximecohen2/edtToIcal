#!/usr/bin/env python3
# coding: utf-8

import argparse
import os
from datetime import date, timedelta, datetime
import requests
from lxml import html
from icalendar import Calendar, Event

EDT_LINK = "https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=pos" \
           "EDTBEECOME&serverid=C&Tel={login}&date={date}"

EDT_MONDAY_COL = "103"
EDT_TUESDAY_COL = "122"
EDT_WEDNESDAY_COL = "141"
EDT_THURSDAY_COL = "161"
EDT_FRIDAY_COL = "180"
EDT_DAYS_COL = [EDT_MONDAY_COL, EDT_TUESDAY_COL, EDT_WEDNESDAY_COL, EDT_THURSDAY_COL, EDT_FRIDAY_COL]

EVENT_SUMMARY_NAME = "summary"
EVENT_DTSTART_NAME = "dtstart"
EVENT_DTEND_NAME = "dtend"
EVENT_DESCRIPTION_NAME = "description"
EVENT_LOCATION_NAME = "location"

DATA_XPATH = "//div[@class=\"Case\" and contains(@style, \"left:{col}\")]"
DATA_SUMMARY_XPATH = ".//td[@class=\"TCase\"]/text()"
DATA_TIME_XPATH = ".//td[@class=\"TChdeb\"]/text()"
DATA_PROF_XPATH = ".//td[@class=\"TCProf\"]/text()"
DATA_LOCATION_XPATH = ".//td[@class=\"TCSalle\"]/text()"

NO_TEACHER_MSG = "(En autonomie)"
TEACHER_MSG = "Intervenant: {teacher}"


def parse_args():
    today = date.today()
    today += timedelta(days=-today.weekday(), weeks=1)
    parser = argparse.ArgumentParser(
        description="Récupère l'emplois du temps de l'étudiant et le retourne au format iCal",
        usage="%(prog)s <StudentLogin> [OPTIONS]")
    parser.add_argument("login", metavar="StudentLogin", help="Login de l'étudiant")
    parser.add_argument("-n", "--filename", help="Nom du fichier", default="edt.ics")
    parser.add_argument("-t", "--target-directory", help="Destination du fichier (défaut: \"./\")", default="./")
    parser.add_argument(
        "-d", "--date",
        help="Date d'une journée de la semaine cible (défaut: aujourd'hui) (ex: 25/12/2000)",
        default=str(date.today().strftime("%d/%m/%Y")))
    parser.add_argument(
        "-w", "--number-week",
        help="Nombre de semaine à récupérer à partir de la date",
        default=1, type=int)
    args = parser.parse_args()
    assert(os.path.exists(args.target_directory) is True), "Error: Target folder doesn't exist."
    return args


def event_generator(args):
    for nb in range(args.number_week):
        b_week = datetime.strptime(args.date, "%d/%m/%Y")
        b_week -= timedelta(days=b_week.weekday())
        b_week += timedelta(weeks=nb)
        page = requests.get(EDT_LINK.format(login=args.login, date=b_week.strftime("%m/%d/%Y")))
        assert(page.status_code == 200), "Error: Can't connect to the page"
        tree = html.fromstring(page.content.decode('utf8'))
        for d in range(len(EDT_DAYS_COL)):
            d_date = b_week + timedelta(days=d)
            for data in tree.xpath(DATA_XPATH.format(col=EDT_DAYS_COL[d])):
                event = Event()
                event.add(EVENT_SUMMARY_NAME, data.xpath(DATA_SUMMARY_XPATH))
                period = data.xpath(DATA_TIME_XPATH)[0].split(' - ')
                assert (len(period) == 2), "Error: Can't get the time in the event"
                s_value = period[0].split(':')
                event.add(EVENT_DTSTART_NAME, d_date.replace(hour=int(s_value[0]), minute=int(s_value[1])))
                e_value = period[1].split(':')
                event.add(EVENT_DTEND_NAME, d_date.replace(hour=int(e_value[0]), minute=int(e_value[1])))
                event.add(EVENT_LOCATION_NAME, data.xpath(DATA_LOCATION_XPATH))
                teacher = data.xpath(DATA_PROF_XPATH)
                event.add(EVENT_DESCRIPTION_NAME,
                          TEACHER_MSG.format(teacher=teacher[0]) if len(teacher) == 2 else NO_TEACHER_MSG)
                yield event


def ical_to_file(args, calendar):
    filename = os.path.join(args.target_directory, args.filename)
    with open(filename, "wb") as file:
        file.write(calendar.to_ical())


def main():
    args = parse_args()
    calendar = Calendar()
    for event in event_generator(args):
        calendar.add_component(event)
    ical_to_file(args, calendar)


if __name__ == '__main__':
    main()
