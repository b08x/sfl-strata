#!/usr/bin/env python3
"""Select the configured private runtime without downloading at MCP startup."""
import sys,os
from pathlib import Path
from runtime import python_path
service=sys.argv[1]
if service not in ('archive','review_packets'):raise SystemExit('Unknown service')
script=Path(__file__).with_name('archive_mcp.py' if service=='archive' else 'review_mcp.py')
python=python_path()
if not python.exists():
 try:import jsonschema
 except ImportError:raise SystemExit('Run python3 configure.py in the sfl-strata plugin directory to prepare its runtime.')
 python=Path(sys.executable)
os.execv(str(python),[str(python),str(script),*sys.argv[2:]])
