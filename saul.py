#!/usr/bin/env python3

from histo2svg import *

def saul():
    # Initialise Grid
    timespan('1976-10-29','2017-06-20')

    # Hardcoded Events
    residence('1991-06-20', '1993-11-20', 'Dorcol, Beograd', class_='g9', style='opacity: 0.5')
#    for y in range(1994, 2009):
#        residence('%s-07-01' % y, '%s-08-31' % y, '', class_='g9', style='opacity: 0.5')
#
#    weekday('2016-02-20', '2016-12-31', 9, 21, 'Grad school', class_='o2')
#    weekend('2016-02-20', '2016-04-05', 50, 'Tower of Hanoi', class_='u7')

main(saul, 'saul.svg')
