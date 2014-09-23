from math import pi
minw = -180
maxw = 180
incr = 5
eps = 0.1

w = minw
s = "WaveDir = {"
while w <= maxw:
    ww = w
    if (w <= -180):
        ww += eps
    if (w >= 180):
        ww -= eps
    ww = (pi/180.0 * ww)
    s= "%s %f" % (s, ww)
    w += incr
    if (w <= maxw):
        s = "%s, " % s

s = "%s}" % s

print s
