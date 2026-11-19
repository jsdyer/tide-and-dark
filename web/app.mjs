import {evaluate,search,localDay} from './model.mjs';
const $=id=>document.getElementById(id);
const node=(tag,text)=>{const el=document.createElement(tag);el.textContent=text;return el};
const ids=['station','from','days','sun','moon','below','near'];
let data,station,filter,matches=[];
function clock(ts,day=false) {
  return new Intl.DateTimeFormat('en-CA',{timeZone:station.zone,hour:'numeric',minute:'2-digit',...(day?{month:'short',day:'numeric'}:{})}).format(ts);
}
function inspect(result) {
  const samples=evaluate(station,result.low,filter,window.SunCalc).samples, centre=samples[(samples.length-1)/2];
  $('inspect').hidden=false;$('chosen').textContent=station.name+' · '+clock(centre.ts,true);
  $('explain').textContent='At the modeled low, the solar altitude is '+centre.sun.toFixed(1)+'° and the lunar altitude is '+centre.altitude.toFixed(1)+'°. The estimated water level is '+(result.low[1]/100).toFixed(2)+' m relative to model mean.';
  $('left').textContent=clock(samples[0].ts);$('right').textContent=clock(samples.at(-1).ts);
  $('strip').replaceChildren(...samples.map(s=>{const el=node('i','');el.className=s.hit?'hit':'';el.style.height=Math.min(100,Math.max(3,-s.sun/90*100))+'%';el.title=clock(s.ts)+' · '+s.sun.toFixed(1)+'°';return el}));
}
function render() {
  station=data.stations.find(s=>s.id===$('station').value);
  filter={from:$('from').value,days:+$('days').value,sun:+$('sun').value,moon:+$('moon').value,below:$('below').value==='below',near:+$('near').value};
  if(!$('from').validity.valid||!filter.from){$('results').hidden=true; $('status').textContent='Choose a date within the published range '+data.start+' to '+data.through+'.';return}
  matches=search(station,filter,window.SunCalc);
  $('results').hidden=false;
  $('status').textContent='Tide estimates '+data.start+' to '+data.through+' · Constants retrieved '+data.retrieved;
  $('heading').textContent=matches.length+' matching '+(matches.length===1?'window':'windows');
  $('coverage').textContent=station.name+' · '+station.zone+' · Five-minute samples near each low. '+(matches.length?'Select a date to inspect the sky.':'Try a wider date range, brighter twilight or a larger illuminated fraction.')+(Date.parse(filter.from)+filter.days*86400000>Date.parse(data.through)+86400000?' Results end at the last available prediction.':'');
  $('provenance').textContent='At '+station.name+', the underlying gauge record runs from '+station.observed_from+' to '+station.observed_to+' (day/month/year). Hart-Davis, Dettmering and Seitz published the TICON-3 constants under CC BY 4.0. This tool reconstructs twelve tidal constituents.';
  $('rows').replaceChildren(...matches.map(r=>{
    const tr=node('tr',''),date=node('td',''),button=node('button',localDay(r.low[0]*60000,station.zone));
    button.addEventListener('click',()=>{inspect(r);$('inspect').scrollIntoView({block:'start'})});date.append(button);
    tr.append(date,node('td',clock(r.start,true)+' – '+clock(r.end,true)),node('td',clock(r.low[0]*60000)+' · '+(r.low[1]/100).toFixed(2)+' m'),node('td',r.moon.toFixed(0)+'%'));return tr
  }));
  $('download').disabled=!matches.length;$('inspect').hidden=!matches.length;if(matches.length)inspect(matches[0]);
  const url=new URL(location.href);for(const id of ids)url.searchParams.set(id,$(id).value);history.replaceState(null,'',url);
}
$('download').addEventListener('click',()=>{
 const iso=t=>new Date(t).toISOString();
 const rows=[['station','time_zone','window_start_UTC','window_end_UTC','low_UTC','model_height_m','moon_lit_percent_at_low'],...matches.map(r=>[station.name,station.zone,iso(r.start),iso(r.end),iso(r.low[0]*60000),(r.low[1]/100).toFixed(2),r.moon.toFixed(2)])];
 const a=node('a','');const url=URL.createObjectURL(new Blob([rows.map(r=>r.join(',')).join('\r\n')],{type:'text/csv'}));a.href=url;a.download='tidal-photo-windows.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)
});
async function start(){
 const response=await fetch('./tides.json');if(!response.ok)throw Error('Unavailable');data=await response.json();
 for(const s of data.stations)$('station').add(new Option(s.name+' · '+s.province,s.id));
 $('from').min=data.start;$('from').max=data.through;
 const today=localDay(Date.now(),'America/Halifax');$('from').value=today<data.start?data.start:today>data.through?data.start:today;
 const query=new URLSearchParams(location.search);
 for(const id of ids){const el=$(id),v=query.get(id);if(id==='from'){if(v&&/^\d{4}-\d\d-\d\d$/.test(v)&&v>=data.start&&v<=data.through)el.value=v}else if([...el.options].some(o=>o.value===v))el.value=v;el.addEventListener('change',render)}
 render();
}
start().catch(()=>{$('status').textContent='The tide edition could not be read. Reload this page to try again.'});
