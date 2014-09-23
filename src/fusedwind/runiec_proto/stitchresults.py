import sys

base = sys.argv[1]
nfiles = int(sys.argv[2])
outname = sys.argv[3]
fno = 0

fout = file(outname, "w")

print "joining %d files named %s.0 to %s.%d" % (nfiles, base, base,nfiles-1)
for fno in range(nfiles):
    fname = "%s.%d" % (base,fno)
    lines=file(fname).readlines()
    if (fno == 0):
        fout.write(lines[0])
    for cnt in range(1,len(lines)):
        fout.write(lines[cnt])

fout.close()
