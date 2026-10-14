export type Event={id:string;timestamp:string;type:string;account:string;sourceIp:string;asset:string;technique:string};
export type Incident={id:string;title:string;kind:string;severity:string;status:string;asset:string;account:string;sourceIp:string;technique:string;createdAt:string;description:string;events:Event[];playbook:boolean[]};
export type State={schemaVersion:number;mode:string;clock:string;events:Event[];incidents:Incident[];runs:string[];audit:{id:string;at:string;action:string;actor:string}[]};
export function detectTakeovers(events:Event[]){
 const ordered=[...new Map(events.map(e=>[e.id,e])).values()].sort((a,b)=>Date.parse(a.timestamp)-Date.parse(b.timestamp)||a.id.localeCompare(b.id));
 return ordered.filter(e=>e.type==='login_success').flatMap(success=>{
  const same=ordered.filter(e=>e.type==='login_failed'&&e.account===success.account&&e.sourceIp===success.sourceIp&&Date.parse(e.timestamp)<Date.parse(success.timestamp));
  const last=same.at(-1);if(!last||Date.parse(success.timestamp)-Date.parse(last.timestamp)>120000)return [];
  const window=same.filter(e=>Date.parse(last.timestamp)-Date.parse(e.timestamp)<=600000);
  return window.length>=5?[{successId:success.id,events:[...window,success]}]:[];
 });
}
const scenarios:Record<string,[string,string,string,string]>={brute_force:['Udane logowanie po serii błędów','critical','T1110','login_failed'],phishing:['Kampania phishingowa: fałszywa faktura','high','T1566.001','email_flagged'],ransomware:['Masowa zmiana plików na DEMO-WS-07','critical','T1486','file_change'],lateral:['Nietypowe sesje zdalne między hostami','high','T1021','remote_session']};
function audit(s:State,action:string){s.audit.unshift({id:`AUD-${s.audit.length+1}`,at:s.clock,action,actor:'Analityk DEMO'});}
export function reduce(s:State,path:string,b:Record<string,unknown>){
 if(path==='/api/simulate'){
  const run=String(b.run_id);if(s.runs.includes(run))return;
  const kind=String(b.scenario);let [title,severity,technique,type]=scenarios[kind];
  const start=Date.parse(s.clock)+60000;const count=kind==='brute_force'?7:4;
  const events=Array.from({length:count},(_,i)=>({id:`SIM-${run}-${i}`,timestamp:new Date(start+i*45000).toISOString().replace('.000Z','Z'),type:kind==='brute_force'&&i===6?'login_success':type,account:`demo-user-${String(s.runs.length+1).padStart(2,'0')}`,sourceIp:'198.51.100.42',asset:'DEMO-WS-07',technique}));
  if(kind==='brute_force'&&!detectTakeovers(events).length){title='Seria nieudanych logowań';severity='medium';}
  s.clock=events.at(-1)!.timestamp;s.events.push(...events);s.runs.push(run);
  s.incidents.unshift({id:`INC-${1043+s.runs.length-1}`,title,kind,severity,status:'new',asset:'DEMO-WS-07',account:events[0].account,sourceIp:events[0].sourceIp,technique,createdAt:s.clock,description:'Scenariusz demonstracyjny. Sprawdź dowody, prześledź chronologię i wykonaj kroki playbooka. Wszystkie zdarzenia są syntetyczne.',events,playbook:[false,false,false]});
  audit(s,`Uruchomiono symulację ${kind}; utworzono ${count} zdarzeń i incydent.`);
 }else if(path.startsWith('/api/incidents/')){
  const inc=s.incidents.find(i=>i.id===path.split('/').at(-1));if(!inc)throw new Error('Nie znaleziono incydentu.');
  if(typeof b.status==='string'){inc.status=b.status;audit(s,`${inc.id}: zmiana statusu na ${b.status}.`);}
  if(typeof b.step==='number'){inc.playbook[b.step]=!inc.playbook[b.step];audit(s,`${inc.id}: zaktualizowano krok playbooka ${b.step+1}.`);}
 }
}
export const severityLabel:Record<string,string>={critical:'Krytyczny',high:'Wysoki',medium:'Średni',low:'Niski'};
export const statusLabel:Record<string,string>={new:'Nowy',investigating:'W analizie',resolved:'Zamknięty'};
