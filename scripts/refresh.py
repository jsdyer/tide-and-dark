"""Generate independent photography tide estimates from TICON-3, CC BY 4.0."""
from datetime import date, datetime, timezone, timedelta
import hashlib
from io import BytesIO
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import numpy as np
from utide._ut_constants import ut_constants
from utide.harmonics import ut_E

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://download.pangaea.de/dataset/951610/files/TICON_3.zip'
# Exact published row coordinates. Keep the coastal gauge when a record has a near duplicate.
STATIONS = [
    ('halifax','Halifax Harbour','NS',44.667,296.417,'America/Halifax'),
    ('yarmouth','Yarmouth','NS',43.830,293.880,'America/Halifax'),
    ('saint-john','Saint John Harbour','NB',45.250,293.940,'America/Moncton'),
    ('point-atkinson','Point Atkinson','BC',49.340,236.750,'America/Vancouver'),
    ('vancouver','Vancouver Harbour','BC',49.290,236.890,'America/Vancouver'),
    ('victoria','Victoria Harbour','BC',48.425,236.630,'America/Vancouver'),
    ('tofino','Tofino','BC',49.150,234.090,'America/Vancouver')]
LINES = ['M2','S2','N2','K2','K1','O1','P1','Q1','M4','MS4','MN4','M6']
const = ut_constants.const
indexes = np.array([list(const.name).index(x) for x in LINES])

def generate(raw, today):
    start = today.replace(day=1)-timedelta(days=32)
    start = start.replace(day=1)
    end = date(today.year+2,1,1)
    with ZipFile(BytesIO(raw)) as archive:
        rows = [l.split() for l in archive.read('TICON_3.txt').decode().splitlines()]
    windows=[]
    for key,name,province,lat,lon,zone in STATIONS:
        picked = {r[2]:r for r in rows if abs(float(r[0])-lat)<.0001 and abs(float(r[1])-lon)<.0001 and r[-1]=='Coastal'}
        if not all(k in picked for k in LINES): raise ValueError(f'Missing constituents for {name}')
        coeff = np.array([float(picked[k][3])*np.exp(-1j*np.deg2rad(float(picked[k][4]))) for k in LINES])
        # UTide date origin is Python proleptic Gregorian ordinal; include an outside day at both ends.
        begin = start.toordinal()-1
        stamps = np.arange(0,(end.toordinal()+1-begin)*144, dtype=np.float64)/144 + begin
        levels=[]
        for t in np.array_split(stamps, max(1,len(stamps)//3600)):
            basis=ut_E(t, np.mean(t), const.freq[indexes], indexes, lat, [False]*4, [])
            levels.extend(np.real(basis @ coeff))
        z=np.asarray(levels)
        minima=np.flatnonzero((z[1:-1]<z[:-2]) & (z[1:-1]<=z[2:]))+1
        lows=[]
        for i in minima:
            # Three-point quadratic interpolation around the 10-minute sampled minimum.
            prev,mid,nex = z[i-1:i+2]
            curvature=prev-2*mid+nex
            shift=(prev-nex)/(2*curvature)
            minute=round((stamps[i]-date(1970,1,1).toordinal())*1440+shift*10)
            when=datetime.fromtimestamp(minute*60,timezone.utc).date()
            if start<=when<end:lows.append([minute,round(mid-(prev-nex)**2/(8*curvature))])
        if len(lows)<(end-start).days:raise ValueError('Low tide series incomplete')
        windows.append(dict(id=key,name=name,province=province,lat=lat,lon=round(lon-360,4),zone=zone,
                            observed_from=picked['M2'][10], observed_to=picked['M2'][11], lows=lows))
    return dict(start=start.isoformat(),through=(end-timedelta(days=1)).isoformat(),retrieved=today.isoformat(),
                records=sum(len(x['lows']) for x in windows),source_sha256=hashlib.sha256(raw).hexdigest(),stations=windows)

if __name__=='__main__':
    with urlopen(URL,timeout=90) as res: raw=res.read()
    data=generate(raw,datetime.now(timezone.utc).date())
    target=ROOT/'web'/'tides.json'
    target.with_suffix('.tmp').write_text(json.dumps(data,separators=(',',':'))+'\n')
    target.with_suffix('.tmp').replace(target)
    (ROOT/'web'/'status.json').write_text(json.dumps({k:v for k,v in data.items() if k!='stations'})+'\n')
    print(data['records'],data['start'],data['through'])
