import test from 'node:test';
import assert from 'node:assert/strict';
import SunCalc from '../web/assets/suncalc.js';
import {readFileSync} from 'node:fs';
import {evaluate,localDay,search} from '../web/model.mjs';
const site=JSON.parse(readFileSync('web/tides.json')).stations[0];
const filter={from:'2026-12-01',days:30,sun:-18,moon:25,near:60,below:false};
test('Local date uses the actual site zone',()=>assert.equal(localDay(Date.parse('2026-12-02T01:00Z'),'America/Halifax'),'2026-12-01'));
test('Saved Canadian station has positive-duration overlaps and each endpoint passes the selected geometry',()=>{
 const startDate=localDay(site.lows[0][0]*60000,site.zone);
 const q={...filter,from:startDate,days:180};const hits=search(site,q,SunCalc);assert.ok(hits.length>0);
 for(const h of hits){assert.ok(h.end>h.start);const ss=evaluate(site,h.low,q,SunCalc).samples.filter(s=>s.ts>=h.start&&s.ts<=h.end);assert.ok(ss.every(x=>x.hit && x.sun<=-18 && x.moon<=25))}
});
