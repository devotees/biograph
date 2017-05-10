#!/usr/bin/env python3

import sys
import svgwrite

def main():
    global d

    fnout = sys.argv[1]

    d = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    d.add_stylesheet('timeline.css', title='some title')

    points = [(0,0), (0,50), (50,50), (50,0)]
    p = d.polygon(points, class_='somepoly')
    d.add(p)

    d.save()

if __name__ == '__main__':
    main()
