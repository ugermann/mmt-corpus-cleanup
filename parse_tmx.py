#!/usr/bin/env python

import sys, os, regex, gzip
from bs4 import BeautifulSoup as BS
from argparse import ArgumentParser 
from datetime import datetime

a = ArgumentParser()
a.add_argument("L",nargs=2,help="source and target languages")
a.add_argument("input", nargs='+', help="Input TMX file(s)")
a.add_argument("-o", help="output dir", default="-", dest="odir")
a.add_argument("-z",dest="gzip",action="store_true", help="output dir",default=False)

opts = a.parse_args(sys.argv[1:])
try:
    os.makedirs(opts.odir)
except:
    pass

def read_tmx_file(fname):
    if ifname == "-":
        ifile = sys.stdin
    elif ifname[-3:] == ".gz":
        ifile = gzip.open(ifname)
    elif ifname[-4:] == ".zip":
        zfile = ZipFile(ifname,"r")
        assert len(zfile.infolist()) == 1
        ifile = zfile.open(zfile.infolist()[0].filename)
    else:
        ifile = open(ifname)
        pass
    return BS(ifile.read().decode('utf8'),'html.parser')

def open_tmp_files(ifile):
    obase = regex.sub(r'.tmx(?:.gz)?','',os.path.basename(ifile))
    ofile = {}
    if opts.odir != "-":
        for tag in opts.L + ['timestamp', 'domain']:
            if opts.gzip:
                ofile[tag] = gzip.open("%s/%s.%s.gz_"%(opts.odir,obase,tag),'w')
            else:
                ofile[tag] = open("%s/%s.%s_"%(opts.odir,obase,tag),'w')
                pass
            pass
        pass
    return ofile

def get_language(t):
    if 'lang' in  t:
        return t['lang']
    return t['xml:lang']

def format_timediff(e):
    h = e.days * 24 + e.seconds/3600
    m = e.seconds%3600/60
    s = e.seconds%60
    return "%3d:%02d:%02d"%(h,m,s)

ctr = 0
for ifname in opts.input:
    print ifname
    ctr += 1
    if ctr%1000 == 0: print ctr
    tmx = read_tmx_file(ifname)
    ofile = open_tmp_files(ifname)
    D = {}
    for tu in tmx.find_all('tu'):
        try:
            if 'changedate' in tu:
                cdate = datetime.strptime(tu['changedate'],"%Y%m%dT%H%M%SZ")
            elif 'creationdate' in tu:
                cdate = datetime.strptime(tu['creationdate'],"%Y%m%dT%H%M%SZ")
            else:
                cdate = datetime.now()
        except:
            cdate = datetime.now()
        domain = [p for p in tu.find_all('prop') if p['type'] == 'tda-type']
        tuv = tu.find_all('tuv')
        tlang = None
        for t in tuv:
            if get_language(t)[:2] == opts.L[0]:
                try:
                    L1 = t.find('seg').string
                except:
                    L1 = None
            else:
                try:
                    L2 = t.find('seg').string
                    tlang = get_language(t)
                except:
                    L2 = None
                pass
            pass
        if L1 == None or L2 == None:
            continue
        L1 = regex.sub('\s+', ' ', L1.strip()).encode('utf8')
        L2 = regex.sub('\s+', ' ', L2.strip()).encode('utf8')
        D.setdefault(L1,[]).append([cdate,L2,tlang])
        pass
    
    for L1,T in D.items():
        if opts.odir != "-":
            print >> ofile[opts.L[0]], L1
            print >> ofile[opts.L[1]], T[-1][1]
        else:
            print
            print L1
            for d,L2,tlang in T:
                e = d - T[0][0]
                print "   ", format_timediff(e), L2, "[%s]"%tlang
                pass
            pass
        pass
    
    for f in ofile.values():
        os.rename(f.name, f.name[:-1])
        pass
    pass
