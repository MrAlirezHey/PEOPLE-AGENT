import streamlit as st
from streamlit_option_menu import option_menu
from core.user_management import create_user, verify_user, save_chat_message, load_chat_history,get_username

import base64
import os
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.langgraph_agent import graph
from agent.explore_mode import search_with_range_filter_and_vector , load_eval_data
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

st.set_page_config(
    page_title="PetaProc People Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    st.markdown("""
        <style>
            #MainMenu, footer, header {
                visibility: hidden;
            }
            .main .block-container {
                padding: 0;
                margin: 0;
                max-width: 100%;
            }
            .login-page-container {
                background-color: #083923;
            }
            .login-card {
                background: #ffffff;
                border-radius: 16px;
                padding: 2rem;
                width: 100%;
                max-width: 400px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            }
            .stButton>button {
                width: 100%;
                border-radius: 8px;
                background-color: #083923;
                color: white;
                font-weight: 600;
                padding: 0.6rem 1rem;
            }
            .circle-img {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                object-fit: cover;
                margin-bottom: 1rem;
                border: 4px solid white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
        </style>
    """, unsafe_allow_html=True)

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="••••••••••", label_visibility="collapsed")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            user, message = verify_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = str(user.user_id)
                st.session_state['username'] = user.username
                st.rerun()
            else:
                st.error(message)

def signup_form():
    with st.form("signup_form"):
        new_username = st.text_input("New Username", placeholder="Choose a username", label_visibility="collapsed")
        new_password = st.text_input("New Password", type="password", placeholder="Create a password", label_visibility="collapsed")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            user, message = create_user(new_username, new_password)
            if user:
                st.success(message)
            else:
                st.error(message)

def login_signup_page():
    load_css()
    st.markdown('<div class="main .block-container login-page-container">', unsafe_allow_html=True)

    logo_path = "static/petaproc_logo.jpg"
    logo_base64 = get_base64_of_bin_file(logo_path)

    st.markdown(f"""
        <div style="text-align:center; padding: 3rem 1rem 2rem 1rem;">
            <img src="data:image/jpeg;base64,{logo_base64}" class="circle-img" alt="logo"/>
            <h1 style="color:white; font-size:2.5rem; font-weight:800; margin-bottom: 1rem;">
                PetaProc People Agent 
            </h1>
            <p style="color:#e5e7eb; font-size:1.1rem; max-width:700px; margin:0 auto;">
                Software Development meets Artificial Intelligence.<br/>
                Find the perfect match for your needs, powered by PetaProc technology.
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.container():
            #st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            selected = option_menu(
                menu_title=None,
                options=["Login", "Sign Up"],
                icons=["box-arrow-in-right", "person-plus-fill"],
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fff"},
                    "icon": {"color": "#083923", "font-size": "18px"},
                    "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#083923", "color": "white"},
                }
            )

            if selected == "Login":
                login_form()
            elif selected == "Sign Up":
                signup_form()

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    st.markdown("""
        <style>
            .main .block-container {
                background-color: #FFFFFF;
                padding: 2rem 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.success(f"Logged in as **{st.session_state['username']}**")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title(f"PetaProc Agent")
    
    selected_mode = option_menu(
        menu_title=None,
        options=["Chat", "Explore Mode"],
        icons=["chat-dots-fill", "compass-fill"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa", "border-radius": "8px"},
            "icon": {"color": "#083923", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#083923"},
        }
    )

    if selected_mode == "Chat":
        st.header("Chat with the Profiler Agent")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What would you like to talk about?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            save_chat_message(
                user_id=st.session_state['user_id'],
                sender='user',
                content=prompt
            )

            state = {
                'user_id': st.session_state['user_id'],
                'messages': [{"role": "user", "content": prompt}],
                'validation_turn': False,
                'user_input_needed': True,
                'end': False
            }
            config={"configurable":{"thread_id":st.session_state['user_id']}}
            # Run the multi-agent graph logic
            graph_response = graph.invoke(state,config=config)
            with st.chat_message("assistant"):
                
                st.markdown(graph_response['messages'][-1].content)
                
                st.session_state.messages.append({"role": "assistant", "content": graph_response['messages'][-1].content})
                
            #save_chat_message(
             #       user_id=st.session_state['user_id'],
             #       sender='agent',
             #       content=response,
            #)ً

    elif selected_mode == "Explore Mode":
        st.header("Explore Mode")
        st.write("This is where users can discover profiles that match their interests.")
        st.info("The profile matching results will be displayed here.")
        if st.button("Find Matching Profiles"):
            response=search_with_range_filter_and_vector(load_eval_data(st.session_state['user_id']))
            for resp in response:
                if resp.id !=st.session_state['user_id']:
                    st.success(get_username(resp.id))

if 'logged_in' in st.session_state and st.session_state['logged_in']:
    main_app()
else:
    login_signup_page()