#!/bin/bash
# usage: with_server.sh <port> <command...>   (serves this directory while the command runs)
PORT=$1; shift
cd "$(dirname "$0")"
python3 -m http.server $PORT >/dev/null 2>&1 &
SP=$!
sleep 1
PORT=$PORT "$@"
RC=$?
kill $SP 2>/dev/null
exit $RC
