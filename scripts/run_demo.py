"""One-command local demo, without Docker. Python >=3.10 and Node >=22 required."""
import argparse, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8101);args=parser.parse_args()
venv=ROOT/'.venv';python=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not python.exists():subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
requirements=ROOT/'backend/requirements.txt';stamp=venv/'demo-requirements.txt'
if not stamp.exists() or stamp.read_text()!=requirements.read_text():
 subprocess.run([str(python),'-m','pip','install','-r',str(requirements)],check=True)
 stamp.write_text(requirements.read_text())
frontend=ROOT/'frontend'
if not (frontend/'node_modules').is_dir():subprocess.run(['npm','ci'],cwd=frontend,check=True)
subprocess.run(['npm','run','build'],cwd=frontend,check=True)
env=os.environ.copy();env['DEMO_STATIC_DIR']=str(frontend/'out')
print(f'Open http://127.0.0.1:{args.port} — synthetic DEMO data only.',flush=True)
subprocess.run([str(python),'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port',str(args.port)],cwd=ROOT,env=env,check=True)
