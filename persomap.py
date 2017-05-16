#!/usr/bin/env python3

import sys
import svgwrite
import datetime
import dateutil.parser


def wraplink(svg_obj, href):
    '''Makes an svg_obj clickable with a link to href.'''

    if href:
        outer = svgwrite.container.Hyperlink(href, target='_blank')
        outer.add(svg_obj)
        svg_obj = outer
    return svg_obj

def addobj(parent, svg_obj):
    ''' Add svg_obj as a subelement to parent'''

    if not parent:
        parent = dwg
    parent.add(svg_obj)

def text(x, y, label, font_size=1.0, color='black', parent=None, href=None):
    '''
    Draws label at (x,y).
    font_size is in ems.
    Optionally, label can link to href.
    '''

    # Coordinates
    x,y = int(x),int(y)
    # 1em - default font size of the document
    # This will scale with different web page sizes

    # Drawing
    p = dwg.g(style='font-size:%.1fem;color:%s'%(font_size, color))
    t = dwg.text(str(label), x=[x+3], y=[y-5])
    p.add(wraplink(t, href))
    addobj(parent, p)

def line(x1, y1, x2, y2, color='grey'):
    '''Draws a colored line from (x1, y1) to (x2, y2).'''

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)

    # Drawing
    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=color))

def rectangle(x1, y1, x2, y2, href=None, parent=None, **kwargs):
    '''
    Draws a rectangle from coordinates (x1, y1) to (x2, y2).
    **kwargs: css styling.
    '''

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]

    # Drawing
    p = dwg.polygon(points, **kwargs)
    addobj(parent, wraplink(p, href))

def width_from_hours(num_days, num_hours):
    '''Given total num_hours spent over num_days, returns the width in pixels'''

    # Input Quality
    assert num_hours <= (num_days * 16)

    options.weekday_hour_width = weekday_hour(10) - weekday_hour(9)
    return  (num_hours/260) * options.weekday_hour_width / (num_days/365)

def weekday_hour(hr):
    '''
    Returns the x-axis coordinate for a weekday time.
    hr must be an int between 8 and 24.
    '''

    # Input Quality
    assert (hr <= 24) and (hr >= 8)

    x_scale = (weekday_right_grid - options.left_grid)/(options.weekday_end_hour-options.weekday_start_hour)
    return options.left_grid + (hr-options.weekday_start_hour)*x_scale

def weekday(start_isodate, end_isodate, start_hour, end_hour, label, **kwargs):
    '''
    Draws a weekday event from (start_hour, start_isodate (YYYY-MM-DD)) to (end_hour, end_isodate (YYYY-MM-DD)).
    **kwargs: css styling
    '''

    # Input Quality
    assert start_isodate < end_isodate

    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)

    # Drawing
    rectangle(x1, y1, x2, y2, **kwargs)
    text(x1, y1, label)

def sleepmate(start_isodate, end_isodate, name_label, **kwargs):
    '''
    Draws pillow cuddle-friends you had from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    **kwargs: css styling.
    '''

    # Input Quality
    assert start_isodate < end_isodate

    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekend_right_grid
    x2 = options.right_grid

    # Drawing
    rectangle(x1, y1, x2, y2, **kwargs)
    text(x1, y1, name_label)

def weekend(start_isodate, end_isodate, hours_per_week, label, **kwargs):
    '''
    Draws a weekend event from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    Width of the drawing is proportional to the hours_per_week invested.
    **kwargs: css styling of main rectangle.
    '''

    # Input Quality
    assert start_isodate < end_isodate

    # Coordinates
    start_date = dateutil.parser.parse(start_isodate)
    end_date = dateutil.parser.parse(end_isodate)
    num_days = (end_date - start_date).days
    num_hours = hours_per_week * num_days / 7

    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekday_right_grid+1
    x2 = x1 + width_from_hours(num_days, num_hours)

    # Drawing
    rectangle(x1, y1, x2, y2, **kwargs)
    text(x1, y1, label)

def event(start_isodate, end_isodate, label, href=None, line_length=20):
    '''
    Draws a circle representing short duration events on the event line.
    Event is centered between start_isodate (YYYY-MM-DD) and end_isodate (YYYY-MM-DD). Size of the circle is proportional to the event duration.
    Set line_length to the amount you want the label offset.
    '''

    # Input Quality
    assert start_isodate <= end_isodate

    # Coordinates
    start_date = parse_date(start_isodate)
    end_date = parse_date(end_isodate)
    event_midpoint = (start_date+end_date)/2
    event_radius = start_date-end_date+5

    # Drawing
    p = dwg.circle((event_line_x, event_midpoint), (end_date-start_date+5), fill='white', stroke='grey')
    dwg.add(wraplink(p, href))
    line(event_line_x+event_radius-3, event_midpoint, event_line_x+event_radius+line_length, event_midpoint)
    text(event_line_x+event_radius+line_length-4, event_midpoint+8, label, font_size=0.6, href=href)


def parse_date(isodate):
    '''Returns the y-axis coordinate for an isodate (YYYY-MM-DD).'''

    parsed_date = dateutil.parser.parse(isodate)
    days_alive = (top_date - bottom_date).days # Total days alive
    day_count = (top_date - parsed_date).days # Number of days into life at which event occurred
    scale = (options.bottom_grid - options.top_grid) / days_alive
    return options.bottom_grid - scale * (days_alive - day_count)

def residence(start_isodate, end_isodate, label, **kwargs):
    '''
    Draws a box of y-axis length = duration of stay at a residence.
    **kwargs: css styling.
    '''

    # Input Quality
    assert start_isodate < end_isodate

    # Coordinates
    start_date = parse_date(start_isodate)
    end_date = parse_date(end_isodate)
    x1 = options.left_grid
    y1 = start_date
    x2 = options.right_grid
    y2 = end_date

    # Drawing
    rectangle(x1, y1, x2, y2, **kwargs)
    if label:
        text(weekday_hour(19), start_date, label, font_size=0.7)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def timespan(start_isodate, end_isodate, **kwargs):
    '''Draws the histomap grid from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).'''

    # Set Options
    timeline_options = dict(
                            left_grid = 50,
                            right_grid = 950,
                            top_grid = 100,    # Today's date
                            bottom_grid = 1200, # Date of birth
                            weekday_start_hour = 7,
                            weekday_end_hour = 24,
                            weekday_hour_width = 30,
                            year_height = None
                            )

    global options
    options = AttrDict(timeline_options)

    global weekday_right_grid, weekend_right_grid, age_left, age_right, event_line_x, top_label_y
    # Timeline X Grid Dimensions
    weekday_right_grid = options.left_grid + options.weekday_hour_width*(options.weekday_end_hour-options.weekday_start_hour)
    weekend_right_grid = weekday_right_grid + (32/260 * options.weekday_hour_width / (7/365))

    age_left = options.right_grid
    age_right = options.right_grid+35
    event_line_x = options.right_grid+50 # X coordinate of the event line

    # Timeline Y Grid Dimensions
    top_label_y = options.top_grid-25


    # Input Quality
    assert start_isodate < end_isodate

    # Set y-axis boundaries of grid
    global bottom_date, top_date
    top_date = dateutil.parser.parse(end_isodate)
    bottom_date = dateutil.parser.parse(start_isodate)

    # Set year ticks on y-axis
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        line(0, dt, options.left_grid, dt)
        text(0,dt, y, font_size=0.9)

    # Set ages on y-axis
    age = 0
    for y in range(bottom_date.year, top_date.year):
        g = svgwrite.container.Group(class_='age')
        dwg.add(g)
        dt = parse_date('%d-%d-%d' % (y, bottom_date.month, bottom_date.day))
        endt = parse_date('%d-%d-%d' % (y+1, bottom_date.month, bottom_date.day))
        rectangle(age_left, dt, age_right, endt, parent=g)
        if age > 0:
            text(age_left-3, dt, str(age), parent=g, font_size=0.8)
        age += 1


    # Set labels on horizontal axis
    # Coordinates
    morning_start = weekday_hour(8)
    afternoon_start = weekday_hour(12)
    evening_start = weekday_hour(18)
    day_end = weekday_hour(24)

    # Drawing
    # Monday to Friday
    text((options.left_grid+weekday_right_grid)/2,options.top_grid-45, 'Mon-Fri')
    line(morning_start, top_label_y+30, morning_start-1, options.top_grid-50)
    text((morning_start+afternoon_start)/2-30, options.top_grid, 'morning')
    line(afternoon_start, top_label_y+30, afternoon_start-1, options.top_grid-30)
    text((afternoon_start+evening_start)/2-30, options.top_grid, 'afternoon')
    line(evening_start, top_label_y+30, evening_start-1, options.top_grid-30)
    text((evening_start+day_end)/2-30, options.top_grid, 'evening')

    # Saturday to Sunday
    line(day_end, top_label_y+30, day_end, options.top_grid-50)
    text((day_end+weekend_right_grid)/2-30,options.top_grid-45, 'Sat-Sun')
    line(weekend_right_grid-1, top_label_y+30, weekend_right_grid-1, options.top_grid-30)

    # ZzzzzzZZZ
    line(options.right_grid, top_label_y+30, options.right_grid, options.top_grid-30)
    text((weekend_right_grid+options.right_grid)/2-15, options.top_grid, 'zzz')

   # Draw the event line
    line(event_line_x, options.top_grid, event_line_x, options.bottom_grid)
    text(options.right_grid, top_label_y, 'Events')


def main(func, fnout):

    global dwg
    dwg = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    dwg.add_stylesheet('timeline.css', title='some title')
    func()
    dwg.save()

def run_tests():
    '''Tests'''

    #test_time_per_pixel_consistency
    assert weekday_hour(10) - weekday_hour(9) == width_from_hours(365, 260)

    print("Tests pass")

if __name__ == '__main__':
    run_tests()
