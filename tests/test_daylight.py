from datetime import datetime,timezone,timedelta
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from refresh_daylight import parse,collect,iso
NOW=datetime(2026,11,25,tzinfo=timezone.utc)
def raw():
    return json.dumps([{'eventDate':iso(NOW-timedelta(days=3)+timedelta(hours=6*i)),'value':1 if i%2 else -0.1,'qcFlagCode':'1'} for i in range(84)]).encode()
class DaylightTests(unittest.TestCase):
    def test_negative_chart_levels_and_extrema_are_preserved(self):
        rows=parse(raw(),NOW,NOW+timedelta(days=14));self.assertTrue(any(r['kind']=='low' and r['height']<0 for r in rows));self.assertTrue(any(r['kind']=='high' for r in rows))
    def test_incomplete_or_invalid_source_fails_before_write(self):
        for data in [b'[]',b'{}',json.dumps([{'eventDate':iso(NOW),'value':999}]*10).encode()]:
            with self.assertRaises(ValueError):parse(data,NOW,NOW+timedelta(days=14))
    def test_config_can_grow_and_prior_smaller_capture_stays_valid(self):
        config=json.loads((Path(__file__).resolve().parents[1]/'web/daylight-config.json').read_text());config['stations']=config['stations'][:1]
        first=collect(config,now=NOW,fetch=lambda _:raw(),pause=lambda _:None)
        config['stations'].append({**config['stations'][0],'id':'extra'})
        second=collect(config,now=NOW,fetch=lambda _:raw(),pause=lambda _:None)
        self.assertEqual(len(first['stations']),1);self.assertEqual(len(second['stations']),2)
