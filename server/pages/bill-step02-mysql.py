import streamlit as st
import requests
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

conn = pymysql.connect(
    host="192.168.219.108",
    user="kyi",
    password=".guppy123!",
    db="demo")

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

    try:
        with conn.cursor() as cursor:
            selection, output = st.columns((0.5, 0.5))
            with selection:
                sql = st.text_input("$\clubs ~~ $ Input SQL Query - KR Test Server: ", \
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


