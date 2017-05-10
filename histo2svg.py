#!/usr/bin/env python3

import sys
import svgwrite
import datetime
import dateutil.parser

left_grid = 50
right_grid = 950
top_grid = 100    # today
bottom_grid = 900 # birthdate

top_date = None
bottom_date = None

def main():
    timespan('1991-06-20','2017-06-20')
    residence('1991-06-20', '1993-11-20', 'Beograd, Srbija', class_='g9')

def timespan(start_datestr, end_datestr):
    global bottom_date, top_date
    top_date = dateutil.parser.parse(end_datestr)
    bottom_date = dateutil.parser.parse(start_datestr)


def parse_date(datestr):
    parsed_date = dateutil.parser.parse(datestr)
    totaldays = (top_date - bottom_date).days
    ndays = (top_date - parsed_date).days
    scale = (bottom_grid - top_grid)/totaldays
    hyp_point = bottom_grid - scale * (totaldays - ndays)
    return hyp_point

def residence(start_date, end_date, address, **kwargs):
    start = parse_date(start_date)
    end = parse_date(end_date)
    points = [(left_grid,start), (right_grid,start), (right_grid,end), (left_grid,end)]
    d.add(d.polygon(points, **kwargs))
    d.add(d.text(address, x=[left_grid], y=[start], style='color:black'))


if __name__ == '__main__':
    fnout = sys.argv[1]

    d = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    d.add_stylesheet('timeline.css', title='some title')

    main()

    d.save()
