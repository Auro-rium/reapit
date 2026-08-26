#!/bin/sh
set -eu
export DISPLAY=:99
Xvfb :99 -screen 0 1440x1100x24 -ac +extension GLX +render -noreset >/tmp/xvfb.log 2>&1 &
fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display :99 -forever -shared -localhost -nopw -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
/usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 >/tmp/novnc.log 2>&1 &
exec uvicorn app:app --host 0.0.0.0 --port 8100
