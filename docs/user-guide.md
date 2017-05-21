# Drawing your persomap

## Getting Started

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
residence(css_color, start_isodate, end_isodate, labl, **kwargs)
```
Draws a box in the grid background of y-axis length which is equal to the duration of stay at a residence. 

`css_color` receives a css coloring class as defined in `timeline.css`.

`**kwargs` is for optional css styling.

