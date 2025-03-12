#
#. ${HOME}/.venv/ndai/bin/activate
#cd ${HOME}/ndai-denhub/server
#
# clean 
echo "- Killing streamlit servers... "
killall -9 streamlit
#
# run 
echo "- Running new streamlit servers... "
streamlit run ndai-denhub.py --server.port 30003 \
    --client.showSidebarNavigation=False &> /dev/null &
#streamlit run ndai-denhub.py --server.port 30003 \
#    --client.showSidebarNavigation=False 
