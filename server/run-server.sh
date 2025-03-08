#
. ${HOME}/.venv/ndai/bin/activate
#
# clean 
echo "- Killing streamlit servers... "
killall -9 streamlit
#
cd ${HOME}/ndai-denhub/server
# run 
echo "- Running new streamlit servers... "
streamlit run ndai-denhub.py --server.port 30003 \
    --client.showSidebarNavigation=False &> /dev/null &
