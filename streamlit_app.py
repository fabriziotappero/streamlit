import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import hashlib

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://unsplash.com/photos/GyDktTa0Nmw/download?force=true&w=1920");
        background-size: cover;
    }
   .sidebar .sidebar-content {
        background: url("https://unsplash.com/photos/GyDktTa0Nmw/download?force=true&w=1920");
        background-size: cover;
    }
    </style>
    """,unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# let's load some data
source = pd.DataFrame(np.cumsum(np.random.randn(100, 3), 0).round(2),
                    columns=['alcohol', 'beer', 'coke'], index=pd.RangeIndex(100, name='x'))

source = source.reset_index().melt('x', var_name='category', value_name='y')

line_chart = alt.Chart(source).mark_line(interpolate='basis').encode(
    alt.X('x', title='Year'),
    alt.Y('y', title='Amount in liters'),
    color='category:N'
).properties(
    title='Sales of consumer goods'
)

# for a better implementation see:
# https://blog.jcharistech.com/2020/05/30/how-to-add-a-login-section-to-streamlit-blog-app/
#
pw=st.text_input("Password:", value="", type="password")
if make_hashes(pw) == st.secrets["PAGE_PASSWORD"]:
    st.text("login successful")
else:
    st.stop()

add_selectbox = st.sidebar.selectbox("Actions",
    ("Analyse Data", "Upload Files","Sign Up","About","Contact"))

st.altair_chart(line_chart, use_container_width=True)


with st.sidebar:
    # slider for hour past midnight
    hour_to_filter = st.slider(label='Hours past midnight:', min_value=0, max_value=22, step=2, value=2)

# setup a 4 column layout
col1, col2, col3, col4 = st.columns(4)

col1.text("col1")
col2.text("col2")
col3.text("col3")
col4.text("col4")

