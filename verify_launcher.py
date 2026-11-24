"""Test Run Python File routing without opening a browser during verification."""
from pathlib import Path
import runpy
import threading
from unittest.mock import patch, Mock
import launch_app

R=Path(__file__).resolve().parent
with patch('launch_app.shutil.which',return_value='uv'):
    args=launch_app.command(R,8522)
    assert args[:4]==['uv','run','--locked','--project']
    assert args[4]==str(R)
    assert args[5:9]==['python','-m','streamlit','run']
    assert str(R/'app.py') in args
with patch('launch_app.shutil.which',return_value=None), patch('launch_app.importlib.util.find_spec',return_value=None):
    try:launch_app.command(R,8522)
    except RuntimeError:pass
    else:raise AssertionError('Missing dependencies not reported')
with (patch('launch_app.urllib.request.urlopen',return_value=Mock(read=lambda:b'ok')),
      patch('launch_app.webbrowser.open') as browser):
    launch_app.open_when_ready('http://127.0.0.1:8522',threading.Event())
    browser.assert_called_once_with('http://127.0.0.1:8522',new=2)
with patch('launch_app.launch',return_value=0) as launcher:
    try:runpy.run_path(str(R/'app.py'),run_name='__main__')
    except SystemExit as e:assert e.code==0
    else:raise AssertionError('Direct app execution failed to route to launcher')
    launcher.assert_called_once()
print('PASS: Python Run-button routing, locked-environment launch and browser readiness')
