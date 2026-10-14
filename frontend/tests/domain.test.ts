import test from 'node:test';import assert from 'node:assert/strict';
import {detectTakeovers,reduce,State,Event} from '../lib/domain';
import seed from '../../datasets/synthetic/seed.json';
const event=(id:string,seconds:number,type='login_failed',account='a',sourceIp='192.0.2.1'):Event=>({id,timestamp:new Date(Date.UTC(2026,0,1)+seconds*1000).toISOString(),type,account,sourceIp,asset:'DEMO',technique:'T1110'});
const failures=()=>Array.from({length:5},(_,i)=>event(String(i),i*60));
test('sorts by event time and deduplicates IDs',()=>{const e=[...failures(),event('s',300,'login_success')];assert.equal(detectTakeovers([...e.reverse(),e[0]]).length,1);});
test('success follows all failures strictly within two minutes',()=>{for(const [seconds,n] of [[240,0],[241,1],[360,1],[361,0]])assert.equal(detectTakeovers([...failures(),event('s',seconds,'login_success')]).length,n);});
test('ten minute failure window includes boundary, excludes excess',()=>{for(const [span,n] of [[600,1],[601,0]])assert.equal(detectTakeovers([0,150,300,450,span].map((x,i)=>event(String(i),x)).concat(event('s',span+1,'login_success'))).length,n);});
test('accounts and IP addresses are isolated',()=>{for(const field of ['account','sourceIp'] as const){const e=failures();e[0][field]='different';assert.equal(detectTakeovers([...e,event('s',300,'login_success')]).length,0);}});
test('duplicate failures do not count twice',()=>{const e=failures().slice(0,4);assert.equal(detectTakeovers([...e,e[0],e[0],event('s',300,'login_success')]).length,0);});
test('simulation is repeatable and request-id idempotent',()=>{const s=structuredClone(seed) as unknown as State;reduce(s,'/api/simulate',{scenario:'brute_force',run_id:'test'});reduce(s,'/api/simulate',{scenario:'brute_force',run_id:'test'});assert.equal(s.events.length,507);assert.equal(s.incidents.length,13);assert.equal(s.incidents[0].severity,'critical');assert.equal(s.incidents[0].id,'INC-1043');});

test('timestamp offsets sort by instant',()=>{const e=failures();e[0].timestamp='2026-01-01T01:00:00+01:00';assert.equal(detectTakeovers([...e,event('s',300,'login_success')]).length,1);});
