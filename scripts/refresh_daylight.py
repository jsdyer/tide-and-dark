#!/usr/bin/env python3
"""Capture CHS high/low predictions for a bounded daylight-planning horizon."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://api-iwls.dfo-mpo.gc.ca/api/v1/stations/'
def iso(d):return d.isoformat(timespec='seconds').replace('+00:00','Z')
def date(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def download(url):
    request=urllib.request.Request(url,headers={'User-Agent':'CoolCode TideAndDark/1.0 (+https://coolcode.ca/tide-and-dark/)','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=35) as response:raw=response.read(2000001)
    if len(raw)>2000000:raise ValueError('CHS source exceeds size limit')
    return raw

def parse(raw,start,end):
    rows=json.loads(raw)
    if not isinstance(rows,list) or not 8<=len(rows)<=200:
        raise ValueError('Missing or oversized high/low prediction series')
    points=[]
    for row in rows:
        t=date(row['eventDate']);v=row['value']
        if t.tzinfo is None or isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not -20<=v<=30:
            raise ValueError('Invalid CHS prediction')
        points.append({'time':iso(t),'height':v,'quality':str(row.get('qcFlagCode','')),'reviewed':row.get('reviewed',False) is True})
    points.sort(key=lambda p:p['time'])
    if len({p['time'] for p in points})!=len(points):raise ValueError('Duplicate CHS extrema')
    result=[]
    # The API supplies extrema without an event label. Classify only a strict
    # local extremum using its neighbours, fetched beyond both display edges.
    for prev,p,nxt in zip(points,points[1:],points[2:]):
        t=date(p['time'])
        if not start<=t<end:continue
        if p['height']<prev['height'] and p['height']<nxt['height']:kind='low'
        elif p['height']>prev['height'] and p['height']>nxt['height']:kind='high'
        else:kind='unclassified'
        result.append({**p,'kind':kind})
    if not result or date(result[0]['time'])>start+timedelta(hours=26) or date(result[-1]['time'])<end-timedelta(hours=26):
        raise ValueError('Incomplete CHS prediction horizon')
    if any(date(b['time'])-date(a['time'])>timedelta(hours=26) for a,b in zip(result,result[1:])):
        raise ValueError('CHS prediction gap')
    return result

def collect(config,now=None,fetch=download,pause=time.sleep):
    now=now or datetime.now(timezone.utc);start=now.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=1)
    days=config.get('days',14)
    if not isinstance(days,int) or not 3<=days<=21:raise ValueError('days must be 3–21')
    end=start+timedelta(days=days+2);stations=[]
    if not 1<=len(config['stations'])<=25:raise ValueError('Configure 1–25 CHS stations')
    seen=set()
    for s in config['stations']:
        if s['id'] in seen or not re.fullmatch('[a-f0-9]{24}',s['station_id']) or not re.fullmatch('[0-9]{5}',s['code']):raise ValueError('Invalid or duplicate CHS station')
        seen.add(s['id'])
        query=urllib.parse.urlencode({'time-series-code':'wlp-hilo','from':iso(start-timedelta(days=1)),'to':iso(end+timedelta(days=1))})
        url=BASE+s['station_id']+'/data?'+query
        raw=fetch(url);events=parse(raw,start,end)
        stations.append({**s,'events':events,'source':url,'source_sha256':hashlib.sha256(raw).hexdigest()})
        pause(2.1) # Fewer than 30 requests/minute, also safe if the watchlist grows.
    return {'schema':1,'retrieved':iso(now),'start':iso(start),'through':iso(end),'datum':'chart datum','source':'Canadian Hydrographic Service IWLS wlp-hilo','stations':stations}

def refresh(root=ROOT):
    config=json.loads((root/'web/daylight-config.json').read_text());data=collect(config)
    target=root/'web/daylight.json';temp=target.with_suffix('.tmp');temp.write_text(json.dumps(data,separators=(',',':'))+'\n');temp.replace(target)
    status={k:data[k] for k in ['schema','retrieved','start','through','source']};status.update(stations=len(data['stations']),records=sum(len(s['events']) for s in data['stations']))
    (root/'web/daylight-status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(f"Captured {status['records']} official predicted extrema for {status['stations']} stations through {status['through']}")
if __name__=='__main__':refresh()
