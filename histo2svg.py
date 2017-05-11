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

weekday_start_hour=8
weekday_end_hour=24

def main():
    timespan('1991-06-20','2017-06-20')
    residence('1991-06-20', '1993-11-20', 'Beograd, Srbija', class_='g9')
    weekday('2016-02-20', '2016-12-31', 9, 21, 'Grad school', class_='o2')


def weekday(start_datestr, end_datestr, start_hour, end_hour, label, **kwargs):
    y1 = parse_date(start_datestr)
    y2 = parse_date(end_datestr)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
    d.add(d.polygon(points, **kwargs))
    d.add(d.text(str(label), x=[x1], y=[y1], stroke='black', style='color:black', **kwargs))

def weekday_hour(h):
    x_scale = (right_grid - left_grid)/14
    return left_grid + (h-8)*x_scale


def timespan(start_datestr, end_datestr):
    global bottom_date, top_date
    top_date = dateutil.parser.parse(end_datestr)
    bottom_date = dateutil.parser.parse(start_datestr)
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        d.add(d.line((0, dt), (left_grid, dt), stroke='grey'))
        d.add(d.text(str(y), x=[0], y=[dt], style='color:black'))

    for h in range(weekday_start_hour, weekday_end_hour+1):
        x = weekday_hour(h)
        d.add(d.line((x, 0), (x, top_grid), stroke='gray'))
        d.add(d.text(str(h), x=[x], y=[top_grid], style='color:black'))


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
