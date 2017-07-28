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
                        legend=True,             # if False, removes legend
                        private=False,           # if False, censors private information
                        top_grid = 100,          # y coordinate of the top grid border
                        left_grid = 50,          # x coordinate of the left grid border
                        right_grid = 1000,       # x coordinate of the right grid border
                        bottom_grid = 1600,      # y coordinate of the bottom grid border
                        weekday_start_hour = 7,  # Time the day starts
                        weekday_end_hour = 24,   # Time the day ends
                        weekday_hour_width = 30, # Number of x pixels per hour in a weekday
                        year_height = 50         # Number of y pixels per year
                        )


## Of Global Importance
color_palette = {           # Color palette to allocate from
    'friend': 'friend',
    'love': 'love',
    'school': 'school',
    'work': 'work',
    'play': 'play',
    'project': 'project',
    'roommate': 'friend',
    'event': 'event',
    'home': 'gray'
}
headers = "type   intensity   label   start_date   end_date   weekday_start   weekday_end   weekend_hours   href   title   slot   rest".split()
residence_colors = {}
saved_memories = []
event_colors = {}

## Helpers
class TypedAttrDict:
    def __init__(self, d):
        object.__setattr__(self, '_opts', d)

    def __getattr__(self, k):
        return self._opts[k]

    def __setattr__(self, k, v):
        self.__setitem__(k, v)

    def __setitem__(self, k, v):
        if k not in self._opts:
            raise Exception('no such option "%s"' % k)
        self._opts[k] = type(self._opts[k])(v)

def private(s, censored=''):
    return s if options.private else censored

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
    'Returns the x-axis coordinate for a weekday time.'

    x_scale = (weekday_right_grid-weekday_left_grid) / (options.weekday_end_hour-options.weekday_start_hour)
    return weekday_left_grid + (hr-options.weekday_start_hour) * x_scale


## Pencil strokes
def text(x, y, label, align=None, parent=None, href=None, **kwargs):
    '''Draws label at (x,y).
    font_size is in ems.
    Optionally, label can link to href.'''

    # Coordinates
    x,y = int(x),int(y)

    # Drawing
    if align is not None:
        add_class(kwargs, align)
    p = dwg.g(**kwargs)
    t = dwg.text(str(label), x = [x+3], y = [y])
    p.add(wrap_link(t, href))
    add_obj(parent, p)

def text_left(x1, y1, x2, y2, label, font_size=0.7, align='middle', parent=None, href=None, **kwargs):
    '''Draws label at coordinate x1, in between coordinates y1 to y2.
    font_size is in ems.
    Optionally, label can link to href.'''

    x = x1
    y = mid(y1, y2) + 10 
    text(x, y, label, None, parent, href, **kwargs)

def text_center(x1, y1, x2, y2, label, align='middle', parent=None, href=None, **kwargs):
    '''Draws label in the center of coordinates (x1, y1) to (x2, y2).
    font_size is in ems.
    Optionally, label can link to href.'''

    x = mid(x1, x2-underhang_offset)
    y = mid(y1, y2)+underhang_offset
    if abs(y2-y1) > abs(x2-x1) and len(label)*10 > abs(x2-x1):
        add_class(kwargs, 'vert')
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
def occurrence(css_color, label, start_isodate, end_isodate, parent=None, href=None, **kwargs):
    '''Draws a circle representing short duration events on the event line.
    Event is centered between start_isodate (YYYY-MM-DD) and end_isodate (YYYY-MM-DD). Size of the circle is proportional to the event duration.'''

    # Input Quality
    assert start_isodate <= end_isodate, (start_isodate, end_isodate)

    # Coordinates
    start_date = parse_date(start_isodate)
    end_date = parse_date(end_isodate)
    event_midpoint = mid(start_date, end_date)
    event_radius = 3

    # Drawing
    add_class(kwargs, css_color)
    p = dwg.circle((event_line_x, event_midpoint), (event_radius), **kwargs)
    add_obj(parent, wrap_link(p, href))
    text(event_line_x + event_radius, event_midpoint+5, label, class_='event', href=href)

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
    x1 = weekday_left_grid - (roommate_width*(slot)+15)
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
    x2 = weekend_right_grid
    y2 = end_date

    # Drawing
    add_class(kwargs, css_color)
    add_class(kwargs, 'residence')
    rectangle(x1, y1, x2, y2, **kwargs)
    if label:
        text_left(options.left_grid, y1-8, weekday_left_grid, y1-15, label,  align='middle')


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
    options = TypedAttrDict(timeline_options)

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
    global underhang_offset, weekday_left_grid, weekday_right_grid, weekend_right_grid, age_left, age_right, event_line_x, top_grid, top_label_y

    underhang_offset = 5               # ensures text does sit below drawn lines
    top_grid = options.top_grid
    top_label_y = top_grid + 5         # y coordinate of where the top labels are placed

    weekday_left_grid = options.left_grid + 250    
    weekday_right_grid = weekday_left_grid + options.weekday_hour_width*(options.weekday_end_hour-options.weekday_start_hour) # Where the weekdays end
    weekend_right_grid = weekday_right_grid + (32/260 * options.weekday_hour_width / (7/365))                                 # Where the weekends end

    age_left = weekend_right_grid          # x coordinate of where the placement of the ages starts
    age_right = weekend_right_grid + 35    # x coordinate of the right border for ages
    event_line_x = weekend_right_grid + 50 # x coordinate of the event line


    # Set year ticks on y-axis
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        line(0, dt, options.left_grid, dt)
        text(0, dt-2, y, class_='yeartick')

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
    label1_y = top_grid-20
    label2_y = top_grid-4
    label_y = mid(label1_y, label2_y)
    text(mid(morning_start, afternoon_start)-50, label1_y, 'weekday', class_="axis_label")
    text(mid(morning_start, afternoon_start)-50, label2_y, 'mornings', class_="axis_label")
    text(mid(afternoon_start, evening_start)-50, label1_y, 'weekday', class_="axis_label")
    text(mid(afternoon_start, evening_start)-50, label2_y, 'afternoons', class_="axis_label")
    text(mid(evening_start, day_end)-50, label1_y, 'weekday', class_="axis_label")
    text(mid(evening_start, day_end)-50, label2_y, 'evenings', class_="axis_label")
    line(morning_start, top_label_y, morning_start-1, top_grid-50)
    line(afternoon_start, top_label_y, afternoon_start - 1, top_grid-30)
    line(evening_start, top_label_y, evening_start-1, top_grid-30)

    # Saturday to Sunday
    text(mid(day_end, weekend_right_grid)-50, label_y, 'weekends', class_="axis_label")
    line(day_end, top_label_y, day_end, top_grid-50)
    line(weekend_right_grid-1, top_label_y, weekend_right_grid-1, top_grid-50)

    # ZzzzzzZZZ
    text(mid(options.left_grid, weekday_left_grid)-125, label_y, 'residences', class_="axis_label")
    text(morning_start-70, label_y, 'flatmates', class_="axis_label")
    line(weekday_left_grid, top_label_y, weekday_left_grid, top_grid-50)

    # Legend
    if options.legend:
        legend_x1 = mid(options.left_grid, weekday_left_grid)-130
        legend_x2 = legend_x1 + width_from_hours(150,100)
        legend_y1 = options.top_grid - 55
        legend_y2 = legend_y1 + (parse_date('%d-%d-%d' % (top_date.year+1, 5, 30)) - parse_date('%d-%d-%d' % (top_date.year, 12, 28)))
        rectangle(legend_x1-20, legend_y1+10, legend_x2+55, legend_y2-14, class_='legend')
        rectangle(legend_x1, legend_y1+3, legend_x2, legend_y2+3, class_="scale")
        text(legend_x1-15, legend_y2-3, '5 hours/week')
        text(legend_x2+3, legend_y2+18, '20 weeks')
        text(legend_x1+3, legend_y1-8, '100')
        text(legend_x1-1, legend_y1+1, 'hours')

    # Draw the event line
    text(age_right, label_y, 'events', class_="axis_label")
    line(event_line_x, top_grid, event_line_x, options.bottom_grid)

    text(weekend_right_grid+20, 15, 'Generated on ' + end_isodate)

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
            residence_colors[label] = color_palette[type] + str(len(residence_colors)+1)
            color = residence_colors[label]
        else:
            color = residence_colors[label]
            label = ''
        if 'class_' in kwargs:
            color = 'blerg'
        return residence(color, label, start_isodate, end_isodate, **kwargs)

    if type in ['event']:
        if label not in event_colors:
            event_colors[label] = color_palette[type] + str(len(event_colors)+1)
            color = event_colors[label]
        else:
            color = event_colors[label]
            label = ''
        if 'class_' in kwargs:
            color = 'blerg'
        return occurrence(color, label, start_isodate, end_isodate, **kwargs)

    # Weekly
    color = color_palette[type] + str(intensity)
    if type in ['roommate']:
        return sleepmate(color, label, start_isodate, end_isodate or top_isodate, **kwargs)
    if not hours:
        return weekday(color, label, start_isodate, end_isodate or top_isodate, weekday_start_hour, weekday_end_hour, **kwargs)
    else:
        return weekend(color, label, start_isodate, end_isodate or top_isodate, hours, **kwargs)


## The nature of memories
def event(name, start_isodate, end_isodate, *args, **kwargs):
    'Any key events or landmarks in your life?'
    return generic('event', 0, name, start_isodate, end_isodate, *args, **kwargs)

def school(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'Where did you study?'
    return generic('school', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def work(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'How have you made a living?'
    return generic('work', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def play(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'When were some moments you stepped back and did something without a goal in mind?'
    return generic('play', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def project(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'Which sort of endeavours did you undertake?'
    return generic('project', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def love(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'With whom have you written a shared story?'
    return generic('love', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def friend(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'Who have you met along the way that has made the journey more pleasant.'
    return generic('friend', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def roommate(intensity, name, start_isodate, end_isodate, *args, **kwargs):
    'With whom have you lived with?'
    return generic('roommate', intensity, name, start_isodate, end_isodate, *args, **kwargs)

def home(name, start_isodate, end_isodate, **kwargs):
    'Where have you lived?'
    return generic('home', 0, name, start_isodate, end_isodate, **kwargs)


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

        elif type in ['home', 'event']:
            generic(type, 0, label, start_isodate, end_isodate, **kwargs)

        # ... then process the rest
        else:
            generic(type, int(intensity), label, start_isodate, end_isodate, weekday_start_hour, weekday_end_hour, hours, **kwargs)

def setup_dwg(fn):
    'Sets up the svg drawing tool.'

    global dwg

    dwg = svgwrite.Drawing(fn, preserveAspectRatio='xMidYMid meet')
    dwg.add_stylesheet('picography.css', title='base devotees css')
    dwg.add_stylesheet('personal.css', title='user custom css')

    pattern1 = dwg.defs.add(dwg.pattern(size=(20, 20), id="pattern1", patternUnits="userSpaceOnUse"))
    pattern1.add(dwg.rect((0, 0), (20, 20)))
    pattern1.add(dwg.line((0, 20), (20, 0)))

    pattern2 = dwg.defs.add(dwg.pattern(size=(8, 8), id="pattern2", patternUnits="userSpaceOnUse"))
    pattern2.add(dwg.rect((0, 0), (8, 8)))
    pattern2.add(dwg.circle((4, 4), 1))

    pattern3 = dwg.defs.add(dwg.pattern(size=(20, 20), id="pattern3", patternUnits="userSpaceOnUse"))
    pattern3.add(dwg.rect((0, 0), (20, 20)))
    pattern3.add(dwg.line((0, 20), (20, 0)))
    pattern3.add(dwg.line((0, 0), (20, 20)))

    pattern4 = dwg.defs.add(dwg.pattern(size=(20, 20), id="pattern4", patternUnits="userSpaceOnUse"))
    pattern4.add(dwg.rect((0, 0), (20, 20)))
    pattern4.add(dwg.line((10, 0), (10, 20)))

    pattern5 = dwg.defs.add(dwg.pattern(size=(20, 20), id="pattern5", patternUnits="userSpaceOnUse"))
    pattern5.add(dwg.rect((0, 0), (20, 20)))
    pattern5.add(dwg.line((0, 20), (20, 20)))


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
