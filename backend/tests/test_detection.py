from datetime import datetime,timedelta,timezone
import pytest
from backend.app.domain import detect_takeovers,simulate
from backend.app.store import fixture
START=datetime(2026,1,1,tzinfo=timezone.utc)
def event(n,seconds,kind='login_failed',account='alpha',ip='192.0.2.1'):
 return {'id':str(n),'timestamp':(START+timedelta(seconds=seconds)).isoformat(),'type':kind,'account':account,'sourceIp':ip,'asset':'DEMO','technique':'T1110'}
def failures():return [event(i,i*60) for i in range(5)]
def test_accepts_out_of_order_and_deduplicates_success():
 events=failures()+[event('s',300,'login_success')]
 assert len(detect_takeovers(list(reversed(events))+[events[-1]]))==1
@pytest.mark.parametrize('seconds,expected',[(240,0),(241,1),(360,1),(361,0)])
def test_success_boundaries(seconds,expected):
 assert len(detect_takeovers(failures()+[event('s',seconds,'login_success')]))==expected
@pytest.mark.parametrize('span,expected',[(600,1),(601,0)])
def test_failure_window_inclusive(span,expected):
 events=[event(i,x) for i,x in enumerate([0,150,300,450,span])]
 assert len(detect_takeovers(events+[event('s',span+1,'login_success')]))==expected
@pytest.mark.parametrize('field,value',[('account','beta'),('sourceIp','192.0.2.2')])
def test_accounts_and_addresses_are_isolated(field,value):
 events=failures();events[0][field]=value
 assert not detect_takeovers(events+[event('s',300,'login_success')])
def test_duplicate_failures_do_not_reach_threshold():
 events=failures()[:4]
 assert not detect_takeovers(events+[events[0]]*6+[event('s',300,'login_success')])
def test_future_failure_not_used():
 assert not detect_takeovers(failures()[:4]+[event(5,400),event('s',300,'login_success')])
def test_simulation_idempotency():
 data=fixture();simulate(data,'brute_force','same-run');simulate(data,'brute_force','same-run')
 assert len(data['incidents'])==13 and len(data['events'])==507
 assert data['incidents'][0]['severity']=='critical'

def test_offsets_are_ordered_by_instant_not_string():
 events=failures();events[0]['timestamp']='2026-01-01T01:00:00+01:00'
 assert len(detect_takeovers(events+[event('s',300,'login_success')]))==1
