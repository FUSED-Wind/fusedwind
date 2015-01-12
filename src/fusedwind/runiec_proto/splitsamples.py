import sys

base = sys.argv[1]
lines=file(base).readlines()
incr = int(sys.argv[2])
hdr = lines[0].strip()
cnt = 1
fno = 0

print "splitting %s into files with no more than %d samples" % (base, incr)

while (cnt < len(lines)):
    fname = "%s.%d" % (base, fno)
    fout = file(fname, "w")
    fout.write("%s\n" % hdr)
    thiscnt = 0
    while (cnt < len(lines) and thiscnt < incr):
        ln = lines[cnt].strip()
        fout.write("%s\n" % ln)
        cnt += 1
        thiscnt += 1
    fout.close()
    fno += 1


for i in range(0,fno):
    print "python openruniec.py -p -c -i int_samples16161616.txt.%d" % i
    print "cp dlcproto.out dlcproto.out.%d" %i

print "## now reassemble"

           
       
