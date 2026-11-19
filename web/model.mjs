export const STEP = 5;
const degrees=180/Math.PI;
export function localDay(date,zone) {
  const parts=new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:zone}).formatToParts(date);
  const pick=k=>parts.find(p=>p.type===k).value;
  return [pick('year'),pick('month'),pick('day')].join('-');
}
export function evaluate(station,low,filter,solar) {
  const samples=[];
  for(let offset=-filter.near;offset<=filter.near;offset+=STEP) {
    const ts=(low[0]+offset)*60000, date=new Date(ts);
    const sun=solar.getPosition(date,station.lat,station.lon).altitude*degrees;
    const moon=solar.getMoonIllumination(date).fraction*100;
    const altitude=solar.getMoonPosition(date,station.lat,station.lon).altitude*degrees;
    samples.push({ts,sun,moon,altitude,hit:sun<=filter.sun && moon<=filter.moon && (!filter.below||altitude<=0)});
  }
  const spans=[];
  for(const s of samples) {
    if(!s.hit)continue;
    const last=spans.at(-1);
    if(last && last.end+STEP*60000===s.ts)last.end=s.ts;
    else spans.push({start:s.ts,end:s.ts});
  }
  return {low,samples,spans:spans.filter(s=>s.end>s.start)};
}
export function search(station, filter, solar) {
  const start=Date.parse(filter.from+'T00:00:00Z'),end=start+filter.days*86400000;
  if(!Number.isFinite(start))return [];
  const first=filter.from,last=new Date(end).toISOString().slice(0,10);
  const matches=[];
  for(const low of station.lows) {
    const ts=low[0]*60000;
    if(ts<start-86400000 || ts>end+86400000)continue;
    const day=localDay(ts,station.zone);
    if(day<first||day>=last)continue;
    const r=evaluate(station,low,filter,solar);
    for(const span of r.spans)matches.push({...span,low,moon:r.samples[(r.samples.length-1)/2].moon});
  }
  return matches;
}
