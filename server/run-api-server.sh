#
if [ "${USER}" == "kyi" ]; then
. ${HOME}/.venv/ndai/bin/activate
cd ${HOME}/ndai-denhub/server
fi
#
if [ $# -eq 1 ]; then
  run_mode=$1
else
  echo "Usage: bash $0 <run_mode>"
  echo "<run_mode>: D(Debug), R(Release)"
  exit;
fi
#
echo "- Killing uvicorn server... "
killall -9 uvicorn
#
cd src
if [ "${run_mode}" == "D" ]; then
  echo " Run in debug mode "
  uvicorn main:app --host 0.0.0.0 --port 30005 
else
  echo " Run in release mode "
  nohup uvicorn main:app --host 0.0.0.0 --port 30005 \
    > /dev/null 2>&1 & 
fi
