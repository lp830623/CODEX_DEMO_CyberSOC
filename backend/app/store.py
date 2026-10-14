"""Schema v1: one revisioned demo snapshot; optimistic updates prevent lost writes."""
from copy import deepcopy
from pathlib import Path
import json
from sqlalchemy import create_engine, Column, Integer, JSON, select, update
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import IntegrityError
Base = declarative_base()
ROOT = Path(__file__).resolve().parents[2]
class Snapshot(Base):
    __tablename__ = "demo_state_v1"
    id = Column(Integer, primary_key=True)
    revision = Column(Integer, nullable=False, default=0)
    payload = Column(JSON, nullable=False)
class Conflict(Exception): pass

def fixture():
    return json.loads((ROOT / "datasets/synthetic/seed.json").read_text())

def connect(url):
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=args)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        if s.get(Snapshot, 1) is None:
            s.add(Snapshot(id=1, revision=0, payload=fixture()))
            try: s.commit()
            except IntegrityError: s.rollback()  # another process seeded first
    return engine

def read(engine):
    with Session(engine) as s:
        row = s.get(Snapshot, 1)
        return {"data": deepcopy(row.payload), "revision": row.revision}

def mutate(engine, fn, expected=None):
    with Session(engine) as s:
        row = s.get(Snapshot, 1)
        revision = row.revision
        if expected is not None and expected != revision: raise Conflict()
        data = deepcopy(row.payload)
        fn(data)
        changed = s.execute(update(Snapshot).where(Snapshot.id == 1, Snapshot.revision == revision).values(payload=data, revision=revision+1))
        if changed.rowcount != 1:
            s.rollback()
            raise Conflict()
        s.commit()
        return {"data": data, "revision": revision+1}

def reset(engine, expected=None):
    def replace(data):
        data.clear()
        data.update(fixture())
    return mutate(engine, replace, expected)
