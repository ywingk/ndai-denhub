#
. ${HOME}/.venv/ndai/bin/activate
cd ${HOME}/ndai-denhub/server
#
echo "- Killing uvicorn server... "
killall -9 uvicorn
#
cd src
#log_fn="../log/api.log"
#
# -- for debug --
#uvicorn main:app --host 0.0.0.0 --port 30005 
#
# -- for release --
nohup uvicorn main:app --host 0.0.0.0 --port 30005 \
    > /dev/null 2>&1 & 

