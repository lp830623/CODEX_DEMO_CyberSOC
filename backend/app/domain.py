from datetime import datetime, timedelta, timezone
from copy import deepcopy

def timestamp(value): return datetime.fromisoformat(value.replace('Z', '+00:00'))
def iso(value): return value.isoformat().replace('+00:00','Z')
def audit(data, message):
    data['audit'].insert(0, {'id':f"AUD-{len(data['audit'])+1}", 'at':data['clock'], 'action':message, 'actor':'Analityk DEMO'})

def detect_takeovers(events):
    """TODO: implement event-time correlation; see docs/presenter-guide.md."""
    return []

SCENARIOS = {
    'brute_force': ('Udane logowanie po serii błędów', 'critical', 'T1110', 'login_failed'),
    'phishing': ('Kampania phishingowa: fałszywa faktura', 'high', 'T1566.001', 'email_flagged'),
    'ransomware': ('Masowa zmiana plików na DEMO-WS-07', 'critical', 'T1486', 'file_change'),
    'lateral': ('Nietypowe sesje zdalne między hostami', 'high', 'T1021', 'remote_session'),
}

def simulate(data, scenario, run_id):
    if run_id in data['runs']: return
    title, severity, technique, event_type = SCENARIOS[scenario]
    start = timestamp(data['clock']) + timedelta(minutes=1)
    account = f"demo-user-{len(data['runs'])+1:02}"
    count = 7 if scenario == 'brute_force' else 4
    events = [{'id':f'SIM-{run_id}-{i}', 'timestamp':iso(start+timedelta(seconds=i*45)), 'type':'login_success' if scenario=='brute_force' and i==6 else event_type, 'account':account, 'sourceIp':'198.51.100.42', 'asset':'DEMO-WS-07', 'technique':technique} for i in range(count)]
    if scenario=='brute_force' and not detect_takeovers(events):
        title, severity = 'Seria nieudanych logowań', 'medium'
    data['clock'] = events[-1]['timestamp']
    data['events'] = data['events'] + events
    data['runs'].append(run_id)
    data['incidents'].insert(0, {'id':f"INC-{1043+len(data['runs'])-1}", 'title':title, 'kind':scenario, 'severity':severity, 'status':'new', 'asset':'DEMO-WS-07', 'account':account, 'sourceIp':'198.51.100.42', 'technique':technique, 'createdAt':data['clock'], 'description': 'Scenariusz demonstracyjny. Sprawdź dowody, prześledź chronologię i wykonaj kroki playbooka. Wszystkie zdarzenia są syntetyczne.', 'events':events, 'playbook':[False,False,False]})
    audit(data, f'Uruchomiono symulację {scenario}; utworzono {count} zdarzeń i incydent.')

def update_incident(data, incident_id, status=None, step=None):
    incident = next(i for i in data['incidents'] if i['id']==incident_id)
    if status is not None:
        incident['status']=status
        audit(data, f'{incident_id}: zmiana statusu na {status}.')
    if step is not None:
        incident['playbook'][step] = not incident['playbook'][step]
        audit(data, f'{incident_id}: zaktualizowano krok playbooka {step+1}.')
