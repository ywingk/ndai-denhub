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
# clean 
echo "- Killing streamlit servers... "
killall -9 streamlit
#
# run 
echo "- Running new streamlit servers... "
if [ "${run_mode}" == "D" ]; then
  echo " Run in debug mode "
  streamlit run ndai-denhub.py --server.port 30003 \
    --client.showSidebarNavigation=False 
else
  echo " Run in release mode "
  streamlit run ndai-denhub.py --server.port 30003 \
    --client.showSidebarNavigation=False &> /dev/null &
fi
