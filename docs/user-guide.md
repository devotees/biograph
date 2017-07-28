# Drawing your picograph

## Minimal Example

```
from picography import *

def alex():

    # Always begin by initialising the grid...
    timespan('2017-02-24','2017-06-13')
    # ...and by adding your homes
    home('womb', '2017-02-04', '2017-06-13', href='')

    # Go wild with the structure and ordering of the rest
    event('2017-02-04', '2017-02-04', 'conceived')
    event('2017-06-13', '2017-06-13', 'miscarried')


    roommate(3, 'mom', '2017-02-04', '2017-06-13') 

    project(2, 'Prenatal appointments', '2017-04-14', '2017-06-13', 15, 17)
    play(3,'Baby Einstein', '2017-03-22', '2017-06-02', hours=10)

make_pico(alex, 'sys.argv[1:]')
```
![](alex.png)

## The Canvas

```
picography.timespan(start_isodate, end_isodate, **kwargs)
```
Initialises the histomap grid from `start_isodate` (YYYY-MM-DD) to `end_isodate` (YYYY-MM-DD).

Optional arguments:
* `legend`: if False, removes the legend
* `private`: if False, censors private information
* `top_grid`: y coordinate of the top grid border
* `left_grid`: x coordinate of the left grid border
* `right_grid`: x coordinate of the right grid border
* `bottom_grid`: y coordinate of the bottom grid border
* `weekday_start_hour` (int): Time the day starts. Defaults to 7.
* `weekday_end_hour` (int): Time the day ends. Defaults to 24.
* `weekday_hour_width`: Number of x pixels per hour in a weekday.
* `year_height`: Number of y pixels per year.

## Memories

### Core components of a memory

For all:
* `name`: the name given to the memory
* `intensity`: 1-3 ; maps to a css colouring class
* `start_isodate`: the starting date of the memory in isoformat (YYYY-MM-DD)
* `end_isodate`: the ending date of the memory in isoformat (YYYY-MM-DD)
* `href`: optional allows you to associate the memory with a link
* `class_`: optional css class containers

For weekday memories:
* `start_hour`: the start time
* `end_hour`: the end time

For weekend and weekly memories:
* `hours`: the number of hours per week

For w+w and roommates:
* `slot`: 0-3 ; indicate the starting position of the memory along the x-axis.

### The nature of memories

```
picography.home(name, start_isodate, end_isodate, **kwargs)
```
Where have you lived?
Draws a box in the grid background of y-axis length which is equal to the duration of stay at a residence.

---

```
picography.roommate(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
With whom have you lived with?

---

```
picography.friend(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
Who have you met along the way who has made the journey more pleasant?

---

```
picography.love(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
With whom have you written a shared story?

---

```
picography.project(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
Which sort of endeavours did you undertake?

---

```
picography.play(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
When were some moments you stepped back and did something without a goal in mind?

---

```
picography.work(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
How have you made a living?

---

```
picography.school(intensity, name, start_isodate, end_isodate, *args, **kwargs)
```
Where did you study?

---

```
picography.event(name, start_isodate, end_isodate, *args, **kwargs)
```
Any keys events or landmarks in your life?

