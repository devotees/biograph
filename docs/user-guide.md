# Drawing your picograph

## Minimal Example

```
from picography import *

def alex():
    # Initialise Grid

    timespan('2017-02-24','2018-01-01')
    event('2017-02-04', 'conceived')
    event('2017-06-13', 'miscarried')

    residence('pastel1','2017-02-04', '2017-06-13', 'womb', href='')

    roommate('u2','2017-02-04', '2017-06-13', 'mom')

    weekday('g3','2017-04-14', '2017-06-13', 15, 17, 'Prenatal appointments')
    weekend('u2','2017-03-22', '2017-06-02', 10, 'Baby Einstein')

main(alex, 'alex.svg')
```

## Elements of the picograph

```
persomap.timespan(start_isodate, end_isodate, **kwargs)
```
Initialises the histomap grid from `start_isodate` (YYYY-MM-DD) to `end_isodate` (YYYY-MM-DD).

Optional arguments:
* `left_grid`: x coordinate of the left grid border
* `right_grid`: x coordinate of the right grid border
* `bottom_grid`: y coordinate of the bottom grid border
* `weekday_start_hour` (int): Time the day starts. Defaults to 7.
* `weekday_end_hour` (int): Time the day ends. Defaults to 24.
* `weekday_hour_width`: Number of x pixels per hour in a weekday.
* `year_height`: Number of y pixels per year. If set, overrides the setting for `bottom_grid`.

---

```
residence(css_color, start_isodate, end_isodate, label, **kwargs)
```
Used to add where you have lived throughout your life.

Draws a box in the grid background of y-axis length which is equal to the duration of stay at a residence.

`css_color` receives a css coloring class as defined in `timeline.css`.

`**kwargs` is for optional css styling.

---

```
event(start_isodate, end_isodate, label, href=None, line_length=20)
```
Used to represent short duration events.

Draws a circle on the event line which is centered between `start_isodate` (YYYY-MM-DD) and `end_isodate`. Size of the circle is proportional to the duration of the event.

Set `line_length` to the amount you want the `label` offset.

---

```
weekend(css_color, start_isodate, end_isodate, hours_per_week, label, justify = 'middle', slot = 0, **kwargs)
```
Allows you to document how you spent your time on weekends. Also can be used for adding weekly commitments that do not fit neatly into a weekday timeslot.

Draws a weekday event from `start_isodate` (YYYY-MM-DD) to `end_isodate` (YYYY-MM-DD). Width of the drawing is proportional to the `hours_per_week` invested.

`css_color` receives a css coloring class as defined in `timeline.css`.

`justify` can be set to 'left' or 'middle'. It left justifies or centers the `label` respectively.

`**kwargs` is for optional css styling.

---

```
sleepmates(css_color, start_isodate, end_isodate, label, slot=0, justify='middle', **kwargs)
```
"Where I lay my head is home." For adding pillow cuddle-friends and roommates.

Draws the shape from `start_isodate` (YYYY-MM-DD) to `end_isodate` (YYYY-MM-DD).

`css_color` recieves a css coloring class as defined in `timeline.css`.

There are four available `slots` for 4 home-mates. You can indicate which one you want occupied by setting `slot` to 0-3.

`justify` can be set to 'left' or 'middle'. It left justifies or centers the `label` respectively.

`**kwargs` is for optional css styling.

---

```
weekday(css_color, start_isodate, end_isodate, start_hour, end_hour, label, justify='middle', **kwargs)
```
Add scheduled weekday time commitments. 

Draws the shape from (`start_hour`, `start_isodate`(YYYY-MM-DD)) to (`end_hour`, `end_isodate` (YYYY-MM-DD)).

`css_color` receives a css coloring class as defined in `timeline.css`.

`justify` can be set to 'left' or 'middle'. It left justifies or centers the `label` respectively.

`**kwargs` is for optional css styling.
