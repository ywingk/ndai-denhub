import streamlit as st
#import requests
import pymysql

# -------------------------------------------------
page_title = "Bill - OpenDental MySQL Client"

st.set_page_config(
    page_title = page_title,
    page_icon="🎁",
    layout="wide",
    menu_items=None
)
# -------------------------------------------------
dent_sites = {}
dent_ids = ['KR', 'NC']

# --- KR server (Kyi) --- 
host = "192.168.219.108"
user='kyi'
pwd = '.guppy123!'
db = 'demo'
dent_sites['KR'] = [host, user, pwd, db]

# --- NC server (Don Lee) ---
host = "75.165.149.223"
user='donlee'
pwd = 'denhub123!'
db = 'demo'
dent_sites['NC'] = [host, user, pwd, db]
# -------------------------------------------------

# -------------------------------------------------
if 'output' not in st.session_state:
    st.session_state.output = ""

# -------------------------------------------------
test_sql = '''
(Example mysql queries - 2025/03/08, Kyi) 
- Get Table Info:
  - describe patient
  - describe claim
  - describe claimproc
- Test Some Queries for Accepting Bill of John Smith:
  - select PatNum from patient where LName='Smith' and FName='john'
  - select ClaimNum from claim where PatNum=15
  - select * from claimproc cp where cp.ClaimNum = '1'
'''
if __name__ == "__main__":
    st.title(page_title)

    dent_id = st.radio("$\clubs ~~ $ Select Dental Office:", dent_ids)
    if dent_id:
        host, user, password, db = dent_sites[dent_id]
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db)
        
    try:
        with conn.cursor() as cursor:
            selection, output = st.columns((0.5, 0.5))
            with selection:
                sql = st.text_input("$\clubs ~~ $ Input SQL Query - "+dent_id+" Server: ", \
                    placeholder="describe claim")
                st.markdown(test_sql)
                if sql:
                    cursor.execute(sql)
                    st.session_state.output = cursor.fetchall()
            with output:
                if st.session_state.output:
                    _res = st.session_state.output
                    st.markdown(f'** output: ')
                    for item in _res:
                        st.markdown(f"- {item}")
    finally:
        conn.close()


