#
if [ "${USER}" == "kyi" ]; then
. ${HOME}/.venv/ndai/bin/activate
cd ${HOME}/ndai-denhub/server
fi
#
# clean 
echo "- Killing streamlit servers... "
killall -9 streamlit
#
# run 
echo "- Running new streamlit servers... "
# -- for debug --
#streamlit run ndai-denhub.py --server.port 30003 \
#    --client.showSidebarNavigation=False 
# -- for runtime --  
streamlit run ndai-denhub.py --server.port 30003 \
    --client.showSidebarNavigation=False &> /dev/null &
