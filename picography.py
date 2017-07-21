#!/usr/bin/env python3

## Thanks to those who came before us
import sys
import svgwrite
import json
import datetime
import dateutil.parser
import argparse


## Grid Options
timeline_options = dict(
                        left_grid = 50,          # x coordinate of the left grid border
                        right_grid = 960,        # x coordinate of the right grid border
                        bottom_grid = 1200,      # y coordinate of the bottom grid border
                        weekday_start_hour = 7,  # Time the day starts
                        weekday_end_hour = 24,   # Time the day ends
                        weekday_hour_width = 30, # Number of x pixels per hour in a weekday
                        year_height = 50       # Number of y pixels per year
                        )


## Of Global Importance
color_palette = {
    'friend': 'friend',
    'love': 'love',
    'school': 'school',
    'work': 'work',
    'play': 'play',
    'project': 'project',
    'roommate': 'friend'
}
headers = "type   intensity   label   start_date   end_date   weekday_start   weekday_end   weekend_hours   href   title   slot   rest".split()
residence_colors = {}
saved_memories = []


## Helpers
class AttrDict(dict):
    '''A recipe which allows you to treat dict keys like attributions.
    dict.key'''

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

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
    'Add svg_obj as a subelement to parent'

    if not parent:
        parent = dwg
    parent.add(svg_obj)

def parse_date(isodate):
    'Returns the y-axis coordinate for an isodate (YYYY-MM-DD).'

    parsed_date = dateutil.parser.parse(isodate)
    days_alive = (top_date - bottom_date).days # Total days alive
    day_count = (top_date - parsed_date).days # Number of days into life at which event occurred
    scale = (options.bottom_grid-top_grid) / days_alive
    return options.bottom_grid - scale*(days_alive-day_count)

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


## Pencil strokes
def text(x, y, label, align=None, parent=None, href=None, **kwargs):
    '''Draws label at (x,y).
    font_size is in ems.
    align can be set to left, middle or right and controls the alignment of the string relative to (x, y).
    Optionally, label can link to href.'''

    # Coordinates
    x,y = int(x),int(y)

    # Drawing
    if align is not None:
        add_class(kwargs, align)
    p = dwg.g(**kwargs)
    t = dwg.text(str(label), x = [x+3], y = [y-5])
    p.add(wrap_link(t, href))
    add_obj(parent, p)

def text_center(x1, y1, x2, y2, label, align='middle', parent=None, href=None, **kwargs):
    '''Draws label in the center of coordinates (x1, y1) to (x2, y2).
    font_size is in ems.
    Optionally, label can link to href.'''

    x = mid(x1, x2-underhang_offset)
    y = mid(y1, y2)+underhang_offset
    if abs(y2-y1) > abs(x2-x1) and len(label)*10 > abs(x2-x1):
        add_class(kwargs, 'vert')
    else:
        y += 5
    text(x, y, label, align, parent, href, **kwargs)

def line(x1, y1, x2, y2, color='grey'):
    'Draws a colored line from (x1, y1) to (x2, y2).'

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)

    # Drawing
    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=color))

def rectangle(x1, y1, x2, y2, href=None, title=None, parent=None, color='rectangle', **kwargs):
    '''Draws a rectangle from coordinates (x1, y1) to (x2, y2).
    **kwargs: css styling.'''

    # Coordinates
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]

    # Drawing
    add_class(kwargs, color)
    p = dwg.polygon(points, **kwargs)
    add_obj(parent, wrap_link(p, href))
    return p


## Where the magic happens
def event(label, start_isodate, end_isodate, href=None, line_length=20):
    '''Draws a circle representing short duration events on the event line.
    Event is centered between start_isodate (YYYY-MM-DD) and end_isodate (YYYY-MM-DD). Size of the circle is proportional to the event duration.
    Set line_length to the amount you want the label offset.'''

    # Input Quality
    assert start_isodate <= end_isodate, (start_isodate, end_isodate)

    # Coordinates
    start_date = parse_date(start_isodate)
    end_date = parse_date(end_isodate)
    event_midpoint = mid(start_date, end_date)
    event_radius = start_date-end_date + 5

    # Drawing
    p = dwg.circle((event_line_x, event_midpoint), (end_date - start_date + 5), fill='white', stroke='grey')
    dwg.add(wrap_link(p, href))
    text(event_line_x + event_radius, event_midpoint + 8, label, class_='event', href=href)

def weekday(css_color, label, start_isodate, end_isodate, start_hour, end_hour, **kwargs):
    '''Draws a weekday event from (start_hour, start_isodate (YYYY-MM-DD)) to (end_hour, end_isodate (YYYY-MM-DD)).
    **kwargs: optional css styling.'''
    end_isodate = end_isodate or top_isodate

    # Input Quality
    assert start_isodate < end_isodate, (start_isodate, end_isodate)

    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)

    # Drawing
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    text_center(x1, y1, x2, y2, label, **kwargs)

def sleepmate(css_color, label, start_isodate, end_isodate, slot=0, **kwargs):
    '''Draws pillow cuddle-friends you had from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    There are four available slots for 4 home-mates. You can indicate which one you want occupied by setting slot to 0-3.
    **kwargs: optional css styling.'''

    end_isodate = end_isodate or top_isodate

    # Input Quality
    assert start_isodate < end_isodate
    roommate_width = width_from_hours(7, 2)
    # Coordinates
    y1 = parse_date(start_isodate)
    y2 = parse_date(end_isodate)
    x1 = weekend_right_grid + (roommate_width*slot)
    x2 = x1 + roommate_width

    # Drawing
    add_class(kwargs, css_color)
    rectangle(x1, y1, x2, y2, **kwargs)
    text_center(x1, y1, x2, y2, label, **kwargs)

def weekend(css_color, label, start_isodate, end_isodate, hours_per_week, slot=0, **kwargs):
    '''Draws a weekend event from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).
    Width of the drawing is proportional to the hours_per_week invested.
    **kwargs: optional css styling.'''

    end_isodate = end_isodate or top_isodate
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
    text_center(x1, y1, x2, y2, label, **kwargs)


def residence(css_color, label, start_isodate, end_isodate, **kwargs):
    '''Draws a box of y-axis length = duration of stay at a residence.
    **kwargs: optional css styling.'''

    end_isodate = end_isodate or top_isodate

    # Input Quality
    assert start_isodate < end_isodate, (start_isodate, end_isodate)

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
        text_center(weekend_right_grid, y1, x2, y2, label, align='middle', class_='residence')


## Canvas
def timespan(start_isodate, end_isodate, **kwargs):
    'Draws the histomap grid from start_isodate (YYYY-MM-DD) to end_isodate (YYYY-MM-DD).'

    # Set options
    timeline_options.update(**kwargs)
    for k, v in kwargs.items():
        generic('option', 0, k, v)

    generic('timespan', 0, '', start_isodate, end_isodate)

    # Allow convenient access of dictionary values (dict.key)
    global options
    options = AttrDict(timeline_options)

    # Set dates
    assert start_isodate < end_isodate
    global bottom_date,top_date
    global bottom_isodate,top_isodate
    top_isodate = end_isodate
    top_date    = dateutil.parser.parse(end_isodate)     # Final recorded day
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

    underhang_offset = 5               # ensures text does sit below drawn lines
    top_grid         = 100             # y coordinate of the top grid border
    top_label_y      = top_grid + 5    # y coordinate of where the top labels are placed

    weekday_right_grid = options.left_grid + options.weekday_hour_width*(options.weekday_end_hour-options.weekday_start_hour) # Where the weekdays end
    weekend_right_grid = weekday_right_grid + (32/260 * options.weekday_hour_width / (7/365))                                 # Where the weekends end

    age_left     = options.right_grid         # x coordinate of where the placement of the ages starts
    age_right    = options.right_grid + 35    # x coordinate of the right border for ages
    event_line_x = options.right_grid + 50    # x coordinate of the event line


    # Set year ticks on y-axis
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        line(0, dt, options.left_grid, dt)
        text(0, dt, y, class_='yeartick')

    # Set ages on y-axis
    age = 0
    for y in range(bottom_date.year, top_date.year):
        g = svgwrite.container.Group(class_='age')
        dwg.add(g)
        dt   = parse_date('%d-%d-%d' % (y, bottom_date.month, bottom_date.day))
        endt = parse_date('%d-%d-%d' % (y+1, bottom_date.month, bottom_date.day))
        rectangle(age_left, dt, age_right, endt, parent=g)
        if age > 0:
            text_center(age_left, dt, age_right, endt, str(age), parent=g, class_='age')
        age += 1


    # Set labels on horizontal axis
    # Coordinates
    morning_start   = weekday_hour(options.weekday_start_hour)
    afternoon_start = weekday_hour(12)
    evening_start   = weekday_hour(18)
    day_end         = weekday_hour(options.weekday_end_hour)

    # Drawing
    # Monday to Friday
    text(mid(options.left_grid, weekday_right_grid)-60, top_grid-45, 'Weekdays')
    text(mid(morning_start, afternoon_start)-30, top_grid, 'morning')
    text(mid(afternoon_start, evening_start)-30, top_grid, 'afternoon')
    text(mid(evening_start, day_end)-30, top_grid, 'evening')
    line(morning_start, top_label_y, morning_start-1, top_grid-50)
    line(afternoon_start, top_label_y, afternoon_start - 1, top_grid-30)
    line(evening_start, top_label_y, evening_start-1, top_grid-30)

    # Saturday to Sunday
    text(mid(day_end, weekend_right_grid)-40, top_grid-45, 'Weekends')
    line(day_end, top_label_y, day_end, top_grid-50)
    line(weekend_right_grid-1, top_label_y, weekend_right_grid-1, top_grid-50)

    # ZzzzzzZZZ
    text(mid(weekend_right_grid, options.right_grid)-15, top_grid-45, 'zzz')
    line(options.right_grid, top_label_y, options.right_grid, top_grid-50)

    # Legend
    legend_x1 = weekend_right_grid
    legend_x2 = legend_x1 + width_from_hours(150,100)
    legend_y1 = parse_date('%d-%d-%d' % (top_date.year+1, 12, top_date.day))
    legend_y2 = parse_date('%d-%d-%d' % (top_date.year+2,  5, top_date.day))
    rectangle(legend_x1, legend_y1, legend_x2, legend_y2)
    text(legend_x2-1, legend_y1, '100 hours (5 hours/week for 5 months)')

    # Draw the event line
    text(age_right, top_label_y-30, 'Events')
    line(event_line_x, top_grid, event_line_x, options.bottom_grid)


## No matter the nature of memories, they all end up here.
def generic(type, intensity, label, start_isodate, end_isodate=None, weekday_start_hour=None, weekday_end_hour=None, hours=None, **kwargs):
    'Processes all of the memories and sends them to the appropriate drawer'

    href  = kwargs['href'] if 'href' in kwargs else ''
    title = kwargs['title'] if 'title' in kwargs else  ''
    slot  = kwargs['slot'] if 'slot' in kwargs else ''
    rest  = json.dumps(kwargs) if kwargs else ''

    saved_memories.append(list(str(x or '') for x in [type, intensity, label, start_isodate, end_isodate, weekday_start_hour, weekday_end_hour, hours, href, title, slot, rest]))

    kwargs.pop('title', None)

    # Do nuffin
    if type in ['timespan', 'option']:
        return

    # Homes we keep returning to are going to be assigned the same colour
    if type in ['home']:
        if label not in residence_colors:
            residence_colors[label] = 'residence%s'%(len(residence_colors)+1)
            color = residence_colors[label]
        else:
            color = residence_colors[label]
            label = ''
        return residence(color, label, start_isodate, end_isodate)

    if type in ['occurrence']:
        return event(label, start_isodate, end_isodate)

    # Weekly
    color = color_palette[type] + str(intensity)
    if type in ['roommate']:
        return sleepmate(color, label, start_isodate, end_isodate or top_isodate, **kwargs)
    if not hours:
        return weekday(color, label, start_isodate, end_isodate or top_isodate, weekday_start_hour, weekday_end_hour, **kwargs)
    else:
        return weekend(color, label, start_isodate, end_isodate or top_isodate, hours, **kwargs)


## The nature of memories
def occurrence(name, start, end, *args, **kwargs):
    'Any key events or landmarks in your life?'
    return generic('occurrence', 0, name, start, end, *args, **kwargs)

def school(intensity, name, start, end, *args, **kwargs):
    'Where did you enter a course of study?'
    return generic('school', intensity, name, start, end, *args, **kwargs)

def work(intensity, name, start, end, *args, **kwargs):
    'How have you made a living?'
    return generic('work', intensity, name, start, end, *args, **kwargs)

def play(intensity, name, start, end, *args, **kwargs):
    'When were some moments you stepped back and did something just for the simple joy of it?'
    return generic('play', intensity, name, start, end, *args, **kwargs)

def project(intensity, name, start, end, *args, **kwargs):
    'Which sorts of visions were you trying to bring to life?'
    return generic('project', intensity, name, start, end, *args, **kwargs)

def love(intensity, name, start, end, *args, **kwargs):
    'With whom have you written a shared story?'
    return generic('love', intensity, name, start, end, *args, **kwargs)

def friend(intensity, name, start, end, *args, **kwargs):
    'Who have you met along the way that made the journey more pleasant.'
    return generic('friend', intensity, name, start, end, *args, **kwargs)

def roommate(intensity, label, start_isodate, end_isodate, *args, **kwargs):
    'With whom have you lived with?'
    return generic('roommate', intensity, label, start_isodate, end_isodate, *args, **kwargs)

def home(label, start_isodate, end_isodate, **kwargs):
    'Where have you lived?'
    return generic('home', 0, label, start_isodate, end_isodate, **kwargs)


## Where the magic begins
def print_to_tsv(fn):
    'Constructs a blueprint.tsv file out of picography function calls.'

    with open(fn, 'w', encoding='utf-8') as fp:
        fp.write('\t'.join(headers) + '\n')
        for memory in saved_memories:
            fp.write('\t'.join(memory) + '\n')

def tsv_to_svg(fn_tsv):
    'Draws a picograph.svg based off of a blueprint.tsv.'

    memories = open(fn_tsv).readlines()

    # Inspects that the blueprint has the correct structure
    saved_headers = memories[0][:-1].split('\t')
    assert saved_headers == headers, saved_headers

    for memory in memories[1:]:
        memory = memory[:-1]
        type, intensity, label, start_isodate, end_isodate, weekday_start_hour, weekday_end_hour, hours, href, title, slot, rest = memory.split('\t')
        kwargs = {}

        if href:  kwargs['href'] = href
        if title: kwargs['title'] = title
        if slot:  kwargs['slot'] = float(slot)
        if rest:  kwargs.update(json.loads(rest))

        if hours:               hours = float(hours)
        if weekday_start_hour:  weekday_start_hour = float(weekday_start_hour)
        if weekday_end_hour:    weekday_end_hour = float(weekday_end_hour)

        # First handle the special cases ...
        if type == 'option':
            assert label in timeline_options, label
            timeline_options[label] = int(start_isodate) # current container for the option value

        elif type == 'timespan':
            timespan(start_isodate, end_isodate)

        elif type in ['home', 'occurrence']:
            generic(type, 0, label, start_isodate, end_isodate)

        # ... then process the rest
        else:
            generic(type, int(intensity), label, start_isodate, end_isodate, weekday_start_hour, weekday_end_hour, hours, **kwargs)

def setup_dwg(fn):
    'Sets up the svg drawing tool.'

    global dwg

    dwg = svgwrite.Drawing(fn, preserveAspectRatio='xMidYMid meet')
    dwg.add_stylesheet('timeline.css', title='some title')

def collect_args(argv):
    '''picography.py -i <input.tsv> -o <output.svg>
    OR someone.py -t -o <output.tsv>
    OR someone.py -o <output.svg>'''

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', dest='input',  default='',    help='input file')
    parser.add_argument('-t', dest='tsv',    default=False, help='save to tsv', action='store_true')
    parser.add_argument('-o', dest='output', default='',    help='output file')

    return parser.parse_args()

def make_pico(func, argv):
    'If passed -t writes a blueprint.tsv. Otherwise, can be invoked to draw a picograph.svg.'

    args = collect_args(argv)

    if args.tsv:
        setup_dwg('')
        func()
        fnout = args.output or (args.input + '.tsv')
        print_to_tsv(fnout)
    else:
        fnout = args.output or (args.input + '.svg')
        setup_dwg(fnout)
        func()
        dwg.save()

    print('output to %s' % fnout)

def main():
    'Draws a (-o) picograph.svg based on a (-i) blueprint.tsv'

    args = collect_args(sys.argv)

    setup_dwg(args.output or (args.input + '.svg'))
    tsv_to_svg(args.input)
    dwg.save()

if __name__ == '__main__':
    main()
