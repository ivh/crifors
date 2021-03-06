#!/usr/bin/env python3

import sys
from astropy.io import fits as F
from openpyxl import load_workbook

wb = load_workbook(sys.argv[1], data_only=True)
cfg = wb['crmcfgWLEN.txt']
rows=list(cfg.rows)
fitskeys= [c.value for c in rows[5]] # 6th row has FITS header names
types= [c.value for c in rows[3]] # 4th row has field type
setting_col = 2       # 3rd column is std setting name
colnames = [c.value for c in rows[0]]

fitsnames = sys.argv[2:]
for fitsname in fitsnames:
    print(fitsname)
    with F.open(fitsname) as hdulist:
        std = hdulist[0].header['HIERARCH ESO INS WLEN ID']
        try:
            assert(len(std.split('/'))==3)
        except:
            print("The input file has no standard-setting info!")
            sys.exit()

        # clear WLEN headers
        for i in range(10):
            for hdu in hdulist:
                for key in hdu.header.keys():
                    if 'WLEN' in key:
                        del hdu.header[key]

        for row in cfg.rows:
            if row[setting_col].value != std:
                continue

            values = [c.value for c in row]
            for key,val,typ in zip(fitskeys,values,types):
                if typ == 'double' and val:
                    val=float(val)
                if not key: continue
                tmp = key.split(':')
                if len(tmp)==1: # no prefix means primary header
                    det = None
                elif len(tmp)==2: # extension is given before colon
                    det,key = tmp
                else:
                    raise ValueError('Unknown key format')
                if key and not '?' in key:
                    if val==None or val=='':
                        continue #skip key if no value!
                    #if 'CENY' in key:
                    #    print(type(val),val)

                    for i,hdu in enumerate(hdulist):
                        k = 'HIERARCH ESO '+key.replace('.',' ')
                        if det is None:
                            hdu.header[k] = val
                        elif hdu.header.get('EXTNAME') == 'CHIP%s.INT1'%det:
                            hdu.header[k] = val
                        

        hdulist.writeto(fitsname, overwrite=True)
