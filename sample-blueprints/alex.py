#!/usr/bin/env python3

from picography import *

def alex():
    # Initialise Grid

    timespan('2017-01-30', '2017-06-13', year_height=900, legend=False)
    event('conceived', '2017-02-04', '2017-02-04')
    event('miscarried', '2017-06-13', '2017-06-13')

    home('womb', '2017-02-04', '2017-06-13', href='')

    roommate(3, 'mom', '2017-02-04', '2017-06-13', class_='mom')

    project(2, 'Prenatal appointments', '2017-04-14', '2017-06-13', 15, 17, class_='bonding')
    play(3, 'Baby Einstein', '2017-03-22', '2017-06-02', hours=10, class_='bonding')

make_pico(alex, sys.argv[1:])
