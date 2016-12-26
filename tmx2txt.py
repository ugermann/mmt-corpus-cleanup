#!/usr/bin/env python

import regex, sys, os, HTMLParser, gzip

p = HTMLParser.HTMLParser()
lang_pat = regex.compile('^<tuv xml:lang="(..).*')
seg_pat = regex.compile('^<seg>(.*)</seg>')

ifname = sys.argv[1]
if ifname[-3:] == ".gz":
    ifile = gzip.open(ifname)
else:
    ifile = open(ifname)
    pass

obase = regex.sub(r'.tmx(?:.gz)?','',ifname)
print obase

ofile = {}
for ltag in sys.argv[2:]:
    ofile[ltag] = open("%s.%s"%(obase,ltag),'w')
    pass

for line in ifile:
    m = lang_pat.match(line)
    if m:
        lang = m.group(1)
    else:
        m = seg_pat.match(line)
        if m:
            if lang not in ofile: continue
            print >>ofile[lang], p.unescape(m.group(1).decode('utf8')).encode('utf8')
        pass
    pass
