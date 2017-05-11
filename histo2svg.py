#!/usr/bin/env python3

import sys
import svgwrite
import datetime
import dateutil.parser

"""
TODO:
    * Store events in a markdown file and write a handler instead of hard-coding them in main.
    * Add weekend horizontal axis.
"""

# Timeline Grid Dimensions
left_grid = 50
right_grid = 950
top_grid = 100    # Today's date
bottom_grid = 900 # Date of birth

sqpx_per_hour = .001 # Amount of square pixels which represent a unit of time

# Time Range
top_date = None # Today's date
bottom_date = None # Date of birth
weekday_start_hour=8
weekday_end_hour=24

def weekday_hour(hr):
    """
    Returns the x-axis coordinate for a weekday time.
    Args:
        hr (int): Represents the time in 24h notation (E.g. 9 --> '9h00').
    Returns:
        int: An x-axis coordinate.
    """
    x_scale = (right_grid - left_grid)/14
    return left_grid + (hr-8)*x_scale

def weekday(start_datestr, end_datestr, start_hour, end_hour, event_label, **kwargs):
    """
    Draws a weekday event.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The event ending date in ISO format (YYYY-MM-DD).
        start_hour(int): The event starting time in 24h notation (E.g. 9 --> '9h00').
        end_hour (int): The event ending time in 24h notation (E.g. 21 --> '21h00').
        event_label (string): The name of the event.
        **kwargs: css styling
    """
    # Coordinates
    y1 = parse_date(start_datestr)
    y2 = parse_date(end_datestr)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
    # Drawing
    draw.add(draw.polygon(points, **kwargs))
    draw.add(draw.text(str(event_label), x=[x1], y=[y1], stroke='black', style='color:black', **kwargs))

def weekend(start_datestr, end_datestr, num_hours, event_label, **kwargs):
    """
    Draws a weekend event.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The event ending date in ISO format (YYYY-MM-DD).
        num_hours (int): The time invested in the event.
        event_label (string): The name of the event.
    """
    # Coordinates
    y1 = parse_date(start_datestr)
    y2 = parse_date(end_datestr)
    x1 = weekday_hour(30)
    x2 = (y2-y1)/(num_hours*sqpx_per_hour) + x1
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
    # Drawing
    draw.add(draw.polygon(points, **kwargs))
    draw.add(draw.text(str(event_label), x=[x2], y=[y1], stroke='black', style='color:black', **kwargs))

def parse_date(datestr):
    """
    Returns the y-axis coordinate for a date.
    Args:
        datestr (string): A date in ISO format (YYYY-MM-DD).
    Returns:
        int: y-axis coordinate.
    """
    parsed_date = dateutil.parser.parse(datestr)
    days_alive = (top_date - bottom_date).days # Total days alive
    day_count = (top_date - parsed_date).days # Number of days into life at which event occurred
    scale = (bottom_grid - top_grid) / days_alive
    return bottom_grid - scale * (days_alive - day_count)

def residence(start_datestr, end_datestr, address, **kwargs):
    """
    Draws a box of y-axis length = duration of stay at a residence.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The ending date of the timeline in ISO format (YYYY-MM-DD).
        address (string): Address of residence.
        **kwargs: CSS stylesheet shenanigans.
    """
    start_y = parse_date(start_datestr)
    end_y = parse_date(end_datestr)
    points = [(left_grid,start_y), (right_grid,start_y), (right_grid,end_y), (left_grid,end_y)]
    draw.add(draw.polygon(points, **kwargs))
    draw.add(draw.text(address, x=[left_grid], y=[start_y], style='color:black'))

def timespan(start_datestr, end_datestr):
    """
    Draws the histomap grid.
    Args:
        start_datestr(string): The starting date of the timeline in ISO format (YYYY-MM-DD).
        end_datestr(string): The ending date of the timeline in ISO format (YYYY-MM-DD).
    """
    # Set y-axis boundaries of grid
    global bottom_date, top_date
    top_date = dateutil.parser.parse(end_datestr)
    bottom_date = dateutil.parser.parse(start_datestr)
    # Set year ticks on y-axis
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        draw.add(draw.line((0, dt), (left_grid, dt), stroke='grey'))
        draw.add(draw.text(str(y), x=[0], y=[dt], style='color:black'))
    # Set hour ticks on x-axis
    for h in range(weekday_start_hour, weekday_end_hour+1):
        x = weekday_hour(h)
        draw.add(draw.line((x, 0), (x, top_grid), stroke='gray'))
        draw.add(draw.text(str(h), x=[x], y=[top_grid], style='color:black'))

def main():
    # Initialise Grid
    timespan('1991-06-20','2017-06-20')
    # Hardcoded Events
    residence('1991-06-20', '1993-11-20', 'Beograd, Srbija', class_='g9')
    weekday('2016-02-20', '2016-12-31', 9, 21, 'Grad school', class_='o2')
    weekend('2016-02-20', '2016-04-05', 50, 'Tower of Hanoi', class_='u7')

if __name__ == '__main__':
    fnout = sys.argv[1]
    draw = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    draw.add_stylesheet('timeline.css', title='some title')
    main()
    draw.save()
