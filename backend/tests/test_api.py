from fastapi.testclient import TestClient
from backend.app.main import create_app
import pytest

@pytest.fixture
def client(tmp_path):
    app=create_app(f"sqlite:///{tmp_path / 'test.db'}")
    with TestClient(app) as c: yield c
    app.state.engine.dispose()

def test_health_and_reset(client):
    assert client.get('/api/health').json()['externalServices'] is False
    original=client.get('/api/state').json()
    reset=client.post('/api/reset',json={'expected_revision':original['revision']})
    assert reset.status_code==200
    assert reset.json()['data']==original['data']
    assert reset.json()['revision']==original['revision']+1

def test_stale_revision_rejected_without_lost_write(client):
    client.post('/api/reset',json={'expected_revision':0})
    assert client.post('/api/reset',json={'expected_revision':0}).status_code==409
    assert client.get('/api/state').json()['revision']==1

def test_export_is_downloadable_json(client):
    response=client.get('/api/export')
    assert response.status_code==200 and response.json()['mode']=='demo'
    assert 'attachment' in response.headers['content-disposition']

def test_simulate_and_status_persist(client):
    response=client.post('/api/simulate',json={'scenario':'brute_force','run_id':'test-run','expected_revision':0})
    assert response.status_code==200
    incident=response.json()['data']['incidents'][0]
    assert incident['severity']=='critical' and len(incident['events'])==7
    response=client.patch(f"/api/incidents/{incident['id']}",json={'status':'resolved','step':0,'expected_revision':1})
    assert response.status_code==200
    saved=client.get('/api/state').json()['data']['incidents'][0]
    assert saved['status']=='resolved' and saved['playbook'][0]
    assert client.patch('/api/incidents/missing',json={'status':'new'}).status_code==404

def test_invalid_input_rejected(client):
    assert client.post('/api/simulate',json={'scenario':'real_attack','run_id':'x'}).status_code==422
    assert client.patch('/api/incidents/INC-1042',json={'step':3}).status_code==422
    assert client.post('/api/reset',json={'secret':'forbidden'}).status_code==422

