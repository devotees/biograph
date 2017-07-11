#!/usr/bin/env python3

import sys
import svgwrite
import datetime
import dateutil.parser

# Grid Options
timeline_options = dict(
                        left_grid = 50,          # x coordinate of the left grid border
                        right_grid = 800,        # x coordinate of the right grid border
                        bottom_grid = 1200,      # y coordinate of the bottom grid border
                        weekday_start_hour = 7,  # Time the day starts
                        weekday_end_hour = 24,   # Time the day ends
                        weekday_hour_width = 30, # Number of x pixels per hour in a weekday
                        year_height = None       # Number of y pixels per year
                        )

def mid(p1, p2):
    'Returns the midpoint between p1 and p2.'

    return (p1+p2) / 2

def wrap_link(svg_obj, href):
    'Makes an svg_obj clickable with a link to href.'

    if href:
        outer = svgwrite.container.Hyperlink(href, target='_blank')
        outer.add(svg_obj)
        svg_obj = outer

    return svg_obj

def add_class(kwargs, cls):
    'Adds a css styling cls to kwargs.'

    if 'class_' in kwargs:
        kwargs['class_'] = kwargs.get('class_') + ' ' + cls
    else:
        kwargs['class_'] = cls

def add_obj(parent, svg_obj):
    ' Add svg_obj as a subelement to parent'

    if not parent:
        parent = dwg
    parent.add(svg_obj)

def text(x, y, label, font_size=1.0,  align=None, parent=None, href=None, **kwargs):
    '''Draws label at (x,y).
    font_size is in ems.
    align can be set to left, middle or right and controls the alignment of the string relative to (x, y).
    Optionally, label can link to href.'''

    # Coordinates
    x,y = int(x),int(y)
    # 1em - default font size of the document
    # This will scale with different web page sizes

    # Drawing
    if align is not None:
        add_class(kwargs, align)
        p = dwg.g(style='font-size:%.1fem;color:%s'%(font_size, 'black'), **kwargs)
    else:
        p = dwg.g(style='font-size:%.1fem;color:%s'%(font_size, 'black'))
    t = dwg.text(str(label), x = [x+3], y = [y-5])
    p.add(wrap_link(t, href))
    add_obj(parent, p)

def text_left(x1, y1, x2, y2, label, font_size=1.0, parent=None, href=None, **kwargs):
    '''Draws label at coordinate x1, in between coordinats y1 to y2.
    font_size is in ems.
    Optionally, label can link to href.'''

    text(x1, mid(y1, y2+underhang_offset), label, font_size, None, parent, href)

def text_center(x1, y1, x2, y2, label,font_size=1.0, parent=None, href=None, **kwargs):
    '''Draws label in the center of coordinates (x1, y1) to (x2, y2).
    font_size is in ems.
    Optionally, label can link to href.'''

    # TODO: detect whether it should be vertical
    if abs(y2-y1) > abs(x2-x1) and len(label) > 4:
        text(mid(x1, x2-underhang_offset), mid(y1, y2)+underhang_offset, label, font_size, 'middle', parent, href, class_='vert')
    else:
        text(mid(x1, x2-underhang_offset), mid(y1, y2)+underhang_offset+5, label, font_size, 'middle', parent, href)

def line(x1, y1, x2, y2, color='grey'):
    'Draws a colored line from (x1, y1) to (x2, y2).'

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)

    # Drawing
    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=color))

def rectangle(x1, y1, x2, y2, href=None, parent=None, color='rectangle', **kwargs):
    '''Draws a rectangle from coordinates (x1, y1) to (x2, y2).
    **kwargs: css styling.'''

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]

    # Drawing
    add_class(kwargs, color)
    p = dwg.polygon(points, stroke='grey', **kwargs)
    add_obj(parent, wrap_link(p, href))
    return p

def width_from_hours(num_days, num_hours):
    'Given total num_hours spent over num_days, returns the width in pixels'

    # Input Quality
    assert num_hours <= (num_days*16)

    options.weekday_hour_width = weekday_hour(10) - weekday_hour(9)
    return  (num_hours/260) * options.weekday_hour_width / (num_days/365)

def weekday_hour(hr):
    '''Returns the x-axis coordinate for a weekday time.
    hr must be an int between 8 and 24.'''

    x_scale = (weekday_right_grid-options.left_grid) / (options.weekday_end_hour-options.weekday_start_hour)
    return options.left_grid + (hr-options.weekday_start_hour) * x_scale

def weekday(css_color, start_isodate, end_isodate, start_hour, end_hour, label, justify='middle', **kwargs):
    '''Draws a weekday event from (start_hour, start_isodate (YYYY-MM-DD)) to (end_hour, end_isodate (YYYY-MM-DD)).
    css_color receives a css coloring class as defined in timeline.css.
    justify --> "left" ^ "middle" in order to left justify or center the label, respectively.
    **kwargs: optional css styling.'''

    # Input Quality
    assert start_isodate < end_isodate

    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)

    # Drawing
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    if justify == 'middle':
        text_center(x1, y1, x2, y2, label, **kwargs)
    elif justify == 'left':
        text_left(x1, y1, x2, y2, label, **kwargs)

def sleepmate(css_color, start_isodate, end_isodate, label,  slot=0, justify='middle',**kwargs):
    '''Draws pillow cuddle-friends you had from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    css_color receives a css coloring class as defined in timeline.css.
    There are four available slots for 4 home-mates. You can indicate which one you want occupied by setting slot to 0-3.
    justify --> "left" ^ "middle" in order to left justify or center the label, respectively.
    **kwargs: optional css styling.'''

    # Input Quality
    assert start_isodate < end_isodate

    offset = (options.right_grid-weekend_right_grid) / 4
    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekend_right_grid + (offset*slot)
    x2 = options.right_grid - (offset*(3-slot))

    # Drawing
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    if justify == 'middle':
        text_center(x1, y1, x2, y2, label, **kwargs)
    elif justify == 'left':
        text_left(x1, y1, x2, y2, label, **kwargs)


def weekend(css_color, start_isodate, end_isodate, hours_per_week, label, justify='middle', slot=0, **kwargs):
    '''Draws a weekend event from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    Width of the drawing is proportional to the hours_per_week invested.
    css_color receives a css coloring class as defined in timeline.css.
    justify --> "left" ^ "middle" in order to left justify or center the label, respectively.
    **kwargs: optional css styling.'''

    # Input Quality
    assert start_isodate < end_isodate

    if slot < 0:
        slot = 0
    elif slot > 4:
        slot = 4

    # Coordinates
    start_date = dateutil.parser.parse(start_isodate)
    end_date = dateutil.parser.parse(end_isodate)
    num_days = (end_date - start_date).days
    num_hours = hours_per_week * num_days / 7

    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekday_right_grid + 1 + width_from_hours(2, slot*2)
    x2 = x1 + width_from_hours(num_days, num_hours)

    # Drawing
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    if justify == 'middle':
        text_center(x1, y1, x2, y2, label, **kwargs)
    elif justify == 'left':
        text_left(x1, y1, x2, y2, label, **kwargs)

def event(start_isodate, end_isodate, label, href=None, line_length=20):
    '''Draws a circle representing short duration events on the event line.
    Event is centered between start_isodate (YYYY-MM-DD) and end_isodate (YYYY-MM-DD). Size of the circle is proportional to the event duration.
    Set line_length to the amount you want the label offset.'''

    # Input Quality
    assert start_isodate <= end_isodate

    # Coordinates
    start_date = parse_date(start_isodate)
    end_date = parse_date(end_isodate)
    event_midpoint = mid(start_date, end_date)
    event_radius = start_date-end_date + 5

    # Drawing
    p = dwg.circle((event_line_x, event_midpoint), (end_date - start_date + 5), fill='white', stroke='grey')
    dwg.add(wrap_link(p, href))
    line(event_line_x + event_radius, event_midpoint, event_line_x + event_radius + line_length, event_midpoint)
    text(event_line_x + event_radius + line_length - 4, event_midpoint + 8, label, font_size=0.6, href=href)


def parse_date(isodate):
    'Returns the y-axis coordinate for an isodate (YYYY-MM-DD).'

    parsed_date = dateutil.parser.parse(isodate)
    days_alive = (top_date - bottom_date).days # Total days alive
    day_count = (top_date - parsed_date).days # Number of days into life at which event occurred
    scale = (options.bottom_grid-top_grid) / days_alive
    return options.bottom_grid - scale*(days_alive-day_count)

def residence(css_color, start_isodate, end_isodate, label, **kwargs):
    '''Draws a box of y-axis length = duration of stay at a residence.
    css_color receives a css coloring class as defined in timeline.css.
    **kwargs: optional css styling.'''

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
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    if label:
        text_center(x1, y1, x2, y2, label, font_size=0.7)

class AttrDict(dict):
    '''A recipe which allows you to treat dict keys like attributions.
    dict.key'''

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def timespan(start_isodate, end_isodate, **kwargs):
    'Draws the histomap grid from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).'

    timeline_options.update(**kwargs)

    # Allow convenient access of dictionary values (dict.key)
    global options
    options = AttrDict(timeline_options)

    # Set dates
    assert start_isodate < end_isodate
    global bottom_date,top_date
    top_date = dateutil.parser.parse(end_isodate)        # Final recorded day
    bottom_date = dateutil.parser.parse(start_isodate)   # First recorded day

    # If year_height is set, it takes priority over bottom_grid
    if options.year_height is not None:
        days_alive = (top_date - bottom_date).days
        num_years = days_alive/365
        options.bottom_grid = num_years * options.year_height

    # Set the bounds of the viewport such that the entire map can be viewed.
    dwg.viewbox(width=options.right_grid+150, height=options.bottom_grid+50)

    # Set grid variables
    global underhang_offset, weekday_right_grid, weekend_right_grid, age_left, age_right, event_line_x, top_grid, top_label_y

    underhang_offset = 5          # ensures text does sit below drawn lines
    top_grid = 100                # y coordinate of the top grid border
    top_label_y = top_grid + 5    # y coordinate of where the top labels are placed

    weekday_right_grid = options.left_grid + options.weekday_hour_width*(options.weekday_end_hour-options.weekday_start_hour) # Where the weekdays end
    weekend_right_grid = weekday_right_grid + (32/260 * options.weekday_hour_width / (7/365))                                 # Where the weekends end

    age_left = options.right_grid          # x coordinate of where the placement of the ages starts
    age_right = options.right_grid + 35    # x coordinate of the right border for ages
    event_line_x = options.right_grid + 50 # x coordinate of the event line


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
            text_center(age_left, dt, age_right, endt, str(age), parent=g, font_size=0.8)
        age += 1


    # Set labels on horizontal axis
    # Coordinates
    morning_start = weekday_hour(options.weekday_start_hour)
    afternoon_start = weekday_hour(12)
    evening_start = weekday_hour(18)
    day_end = weekday_hour(options.weekday_end_hour)

    # Drawing
    # Monday to Friday
    text(mid(options.left_grid, weekday_right_grid), top_grid - 45, 'Mon-Fri')
    line(morning_start, top_label_y, morning_start - 1, top_grid - 50)
    text(mid(morning_start, afternoon_start) - 30, top_grid, 'morning')
    line(afternoon_start, top_label_y, afternoon_start - 1, top_grid - 30)
    text(mid(afternoon_start, evening_start) - 30, top_grid, 'afternoon')
    line(evening_start, top_label_y, evening_start - 1, top_grid - 30)
    text(mid(evening_start, day_end) - 30, top_grid, 'evening')

    # Saturday to Sunday
    line(day_end, top_label_y, day_end, top_grid - 50)
    text(mid(day_end, weekend_right_grid) - 30, top_grid - 45, 'Sat-Sun')
    line(weekend_right_grid - 1, top_label_y, weekend_right_grid - 1, top_grid - 50)

    # ZzzzzzZZZ
    line(options.right_grid, top_label_y, options.right_grid, top_grid-50)
    text(mid(weekend_right_grid, options.right_grid) - 15, top_grid, 'zzz')

   # Draw the event line
    line(event_line_x, top_grid, event_line_x, options.bottom_grid)
    text(age_right, top_label_y-30, 'Events')



def main(func, fnout):

    global dwg
    dwg = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    dwg.add_stylesheet('timeline.css', title='some title')
    func()
    dwg.save()

def run_tests():
    'Tests'

    #test_time_per_pixel_consistency
    assert weekday_hour(10) - weekday_hour(9) == width_from_hours(365, 260)

    print('Tests pass')

if __name__ == '__main__':
    run_tests()
