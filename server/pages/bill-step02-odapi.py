import streamlit as st
import requests

# -------------------------------------------------
page_title = "Bill - OpenDental API"

st.set_page_config(
    page_title = page_title,
    page_icon="🎁",
    layout="wide",
    menu_items=None
)

# -------------------------------------------------
dent_sites = {}
dent_ids = ['TEST', 'KR', 'NC']

# --- Opendental TEST api server --- 
endpoint = "https://api.opendental.com/api/v1"
key='NFF6i0KrXrxDkZHt/VzkmZEaUWOjnQX2z'
dent_sites['TEST'] = [endpoint, key]

# --- Dencomm at KR server ---
endpoint = "http://3.97.57.154:80/api/v1"
key = 'OMbz0ZKVeIjS2XjX/RqmqY2XsW4lzT3B4'
dent_sites['KR'] = [endpoint, key]

# --- DonLee at NC server ---
endpoint = "http://75.165.149.223:30223/api/v1"
key = 'OMbz0ZKVeIjS2XjX/FBO2yrrmvgQciYNP'
dent_sites['NC'] = [endpoint, key]
# -------------------------------------------------

if 'api_res' not in st.session_state:
    st.session_state.api_res = ""
if 'api_req' not in st.session_state:
    st.session_state.api_req = ""


# -------------------------------------------------
if __name__ == "__main__":
    st.title(page_title)
        
    selection, output = st.columns((0.5, 0.5))
    with selection:
      dent_id = st.radio("Select Dental Office:", dent_ids)
      if dent_id:
        api_endpoint, api_key = dent_sites[dent_id]        
        api_headers = eval("{'Authorization': 'ODFHIR "+api_key+"'}")
        get_req = st.text_input("$\clubs ~~ $ GET Request: ", \
            placeholder="patients?LName=Medi")
        
        st.divider()
        test_req = '''
        * Example Procedure of OpenDental API Request 
          - [GET] patients?LName=Medi
            - Get PatNum of Medicaid, Marvin => (9)
          - [GET] claims?PatNum=9   
            - Get ClaimNum => (10) 
          - [GET] claimprocs?PatNum=9&ClaimNum=10  
            - Get ClaimProcNum => (56) 
          - [PUT] claimprocs/56, {"ProcNum": 51, "FeeBilled":"77.0"}  
            - Put with ClaimProcNum and update some data fields 
          - [PUT] ?
            - Finalize 
        '''
        st.markdown(test_req)
        #test_post = '''{"ClaimNum": 0}'''
        #st.code(test_post)
        #st.divider()
        #
        #get_req = st.text_input("$\clubs ~~ $ GET Request: ", \
        #    placeholder="patients?LName=Medi")
        st.divider()
        put_req = st.text_input("$\clubs ~~ $ PUT Request: ", \
                placeholder="claimprocs/56")
        put_data = st.text_input("$\clubs ~~ $ PUT Data: ", \
                placeholder="{'ProcNum':51, 'FeeBilled': '77.0'}")
        #
        if get_req:
            api_url = api_endpoint+"/"+get_req
            response = requests.get(api_url, headers=api_headers) 
            _res = response.json()
            st.session_state.api_req = get_req
            st.session_state.api_res = _res
        #
        if put_req and put_data:
            api_url = api_endpoint+"/"+put_req
            response = requests.put(api_url, headers=api_headers, data=put_data) 
            _res = response.json()
            st.session_state.api_req = put_req + ", " + put_data
            st.session_state.api_res = _res
        #
        st.divider()

        #
        #if _api_url and not _api_put and _api_post:
        #    api_url = api_endpoint+"/"+_api_url
        #    response = requests.post(api_url, headers=api_headers, data=_api_post) 
        #    _res = response.json()
        #    st.session_state.api_req = _api_post
        #    st.session_state.api_res = _res
    
    with output:
        #st.divider()
        if st.session_state.api_res:
            _req = st.session_state.api_req
            _res = st.session_state.api_res
            
            #st.markdown(f'** endpoint url: {api_endpoint}')
            st.markdown(f'** api request: {_req}')

            #st.markdown(f'** api response: {_res}')
            if isinstance(_res, str) or isinstance(_res, dict):
                st.markdown(f'** api response: {_res}')
            else:
                st.markdown(f'** api response: ') 
                for item in _res:
                    st.markdown(f"- {item}")
            
