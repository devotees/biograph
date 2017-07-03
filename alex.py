#!/usr/bin/env python3

from picography import *

def alex():
    # Initialise Grid

    timespan('2017-01-30', '2017-06-13', year_height=1000)
    event('2017-02-04', '2017-02-04', 'conceived')
    event('2017-06-13', '2017-06-13', 'miscarried')

    residence('pastel1', '2017-02-04', '2017-06-13', 'womb', href='')

    sleepmate('u2', '2017-02-04', '2017-06-13', 'm', slot=0)
    sleepmate('u2', '2017-02-04', '2017-06-13', 'o', slot=1)
    sleepmate('u2', '2017-02-04', '2017-06-13', 'm', slot=2)

    weekday('g3', '2017-04-14', '2017-06-13', 15, 17, 'Prenatal appointments', font_size=0.8)
    weekend('u2', '2017-03-22', '2017-06-02', 10, 'Baby Einstein')

main(alex, 'alex.svg')
