import numpy as np
import pandas as pd

import streamlit as st
import hashlib

import gdown
from datetime import date, datetime, time, timedelta
import re

### various functions

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# load a portion of CSV files preserving header
def load_data(URL_DATA,skiprows,nrows):
    data = pd.read_csv(URL_DATA, encoding = "ISO-8859-1", header=0, skiprows=[i for i in range(1,skiprows)], nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

#similar to https://stackoverflow.com/questions/33997361
def dms2dd(s):
    # example2: s = "00°48.1555' S"
    degrees, minutes, direction = re.split('[°\'"]+', s)
    dd = float(degrees) + float(minutes)/60
    if direction in (' S',' W'):
        dd*= -1
    return dd

# download google drive spreadsheet file
def get_gdrive_spreadsheet(doc_id, sheet_id, file_name):
    sheet_url = f'https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}'
    df = pd.read_csv(sheet_url)
    #df.to_csv(file_name)
    return df

# download any google drive file
@st.cache(suppress_st_warning=True)
def get_gdrive_file(_id, file_name):
    gdown.download('https://drive.google.com/uc?id=' + _id, file_name,quiet=True)
    print("loading database file from the cloud...")

##### BEGIN OF THE CODE

# use full width of the page
st.set_page_config(layout="wide")

# change html background
st.markdown(
    """
    <style>
    .reportview-container {
        background: linear-gradient(rgba(255,255,255,1), rgba(255,255,255,1)), url("https://unsplash.com/photos/GyDktTa0Nmw/download?force=true&w=1920");
        background-size: cover;
    }
   .sidebar .sidebar-content {
        background: linear-gradient(rgba(255,255,255,1), rgba(255,255,255,1)), url("https://unsplash.com/photos/GyDktTa0Nmw/download?force=true&w=1920");
        background-size: cover;
    }
    </style>
    """,unsafe_allow_html=True)

# input password field
# for a better implementation see:
# https://blog.jcharistech.com/2020/05/30/how-to-add-a-login-section-to-streamlit-blog-app/
login_win = st.empty()
pw = login_win.text_input("password", value="", type="password")
if make_hashes(pw) == st.secrets["PAGE_PASSWORD"]:
    #login successful
    login_win.empty()
else:
    #login not successful
    st.stop()

_, col2, _ = st.columns(3)
col2.title('BALUERO DATA VIEWER')

# download spreadsheet index file from Google Drive
# in this files are stored all IDs for csv files
doc_id = st.secrets["GOOGLE_DRIVE_DATABASE_ID_SPREADSHEET"]

sheet_id = '0'
df = get_gdrive_spreadsheet(doc_id, sheet_id,'gdrive_index.csv')

# setup a 4 column layout
col1, col2, col3, col4 = st.columns(4)

# slider to select time to show
#start_hour = col1.slider(label='Select time to show', min_value=0, max_value=22, step=2, value=2)
set_time = col1.slider('Set begin time', value=time(00, 00, 00),
                              min_value=time(00, 00, 00),
                              max_value=time(22, 00, 00),
                              step=timedelta(hours=2),
                              format='H:mm')
start_hour = set_time.hour

# work out the number of samples to load for the selected portion of time
start_sample = int(start_hour/2 * 3600) # start samples
number_samples = 3600*2/2 # number of samples equivament to 2h 

# select date
new_date = col2.date_input('Pick a day', date(2021,8,15))

# setup a 4 column layout
#col1, col2 = st.columns(2)

# data info text
txtbox3 = col3.empty()
txtbox4 = col4.empty()
txtbox3.text('Showing 2h worth of data from ' + str(start_hour) + ':00')

# Define local file path (only used with a local csv database)
#B4B_MSG_FILE_LOC  = ('../logs/SystemMea_dp_' + new_date.strftime("%Y_%m_%d") + '.zip')
#KYMA_MSG_FILE_LOC = ('../logs/Kyma/BalueiroSegundo ' + new_date.strftime("%Y-%m-%d") + '.zip')

# search for Google Drive ID for the 3 files to download

# Bound4Blue Allarm File
file_name = 'SystemAlarms_dp_' + new_date.strftime("%Y_%m_%d") + '.zip'
for i,x in enumerate(df['b4b_alarm_file']):
    if file_name in str(x):
        # found element at position i
        b4b_alarm_file_id = df['b4b_alarm_file_id'][i]
        break
    else:
        b4b_alarm_file_id =''

# Kyma Message File
file_name = 'BalueiroSegundo ' + new_date.strftime("%Y-%m-%d") + '.zip'
for i,x in enumerate(df['kyma_msg_file']):
    if file_name in str(x):
        # found element at position i
        kyma_msg_file_id = df['kyma_msg_file_id'][i]
        break
    else:
        kyma_msg_file_id =''

# Bound4Blue Message File
file_name = 'SystemMea_dp_' + new_date.strftime("%Y_%m_%d") + '.zip'
for i,x in enumerate(df['b4b_msg_file']):
    if file_name in str(x):
        # found element at position i
        b4b_msg_file_id = df['b4b_msg_file_id'][i]
        break
    else:
        b4b_msg_file_id =''

# Download the 3 csv files (worth 24h of data each) from Google drive into a tmp folder
if b4b_alarm_file_id:
    get_gdrive_file(b4b_alarm_file_id, 'tmp/b4b_alarm_db.zip')
if kyma_msg_file_id:
    get_gdrive_file(kyma_msg_file_id, 'tmp/kyma_msg_db.zip')
if b4b_msg_file_id:
    get_gdrive_file(b4b_msg_file_id, 'tmp/b4b_msg_db.zip')

# warn user if data is not available for that specific date
if b4b_alarm_file_id=='' or kyma_msg_file_id=='' or b4b_msg_file_id=='':
    #txtbox4.text('Data for ' + new_date.strftime("%Y-%m-%d") + ' is not available.')
    msg = 'Data for ' + new_date.strftime("%Y-%m-%d") + ' is not available.'
    msg = '<p style="color:Red;">'+msg+'</p>'
    txtbox4.markdown(msg, unsafe_allow_html=True)



    print('ERROR loading csv files')
else:
    txtbox4.text('Remote data Loaded successfully.')


# setup a 2 column layout
col1, col2 = st.columns(2)

# show a partial data table starting from the selected time
data = load_data('tmp/b4b_msg_db.zip', start_sample, number_samples) # load selected portion of data 
col1.dataframe(data,height=500) # show table

#if st.checkbox('Plot table data', value=False):
#    chart_data = pd.DataFrame(data,columns=['awa[deg]', 'aws[kn]', 'esail_position[deg]','mode','suctionfan[rpm]'])
#    col1.line_chart(chart_data)

# show a map with lat/long vessel position
start_sample = int(start_hour/15 * 3600) # start samples
number_samples = 3600*2/15 # number of samples equivament to 2h 
data = load_data('tmp/kyma_msg_db.zip',start_sample,number_samples)
data.rename({'latitude (text)':'lat','longitude (text)':'lon'}, axis='columns',inplace=True)
data['lat'] = data['lat'].apply(dms2dd)
data['lon'] = data['lon'].apply(dms2dd)
col2.map(data)
#col2.dataframe(data,height=500) # show table

# TEST PLOT some data
#st.text('TEST: Whole day')
#data_w = load_data(DATA1_LOCATION,0, 3600*24/2) # load whole data 
#chart_data_w = pd.DataFrame(data_w,columns=['awa[deg]', 'aws[kn]', 'esail_position[deg]','mode','suctionfan[rpm]'])
#st.line_chart(chart_data_w)

# load a portion, just 2h, of the data starting from the slider time
start_sample = int(start_hour/2 * 3600) # start samples
number_samples = 3600*2/2 # number of samples equivament to 2h 
data = load_data('tmp/b4b_msg_db.zip', start_sample, number_samples) # load selected portion of data 

# PLOT some data
chart_data = pd.DataFrame(data,columns=['awa[deg]', 'aws[kn]', 'esail_position[deg]'])
chart_data['lasped_time'] = np.arange(0, chart_data.shape[0]*2,2) # add lapsed time column in second
chart_data = chart_data.set_index('lasped_time')
col1.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['sog[kn]', 'flap_pos', 'heel[deg]'])
chart_data['lasped_time'] = np.arange(0, chart_data.shape[0]*2,2) # add lapsed time column in second
chart_data = chart_data.set_index('lasped_time')
col2.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['currentavg[a]', 'power_cons[w]', 'activepowertotal[w]','mode'])
chart_data['lasped_time'] = np.arange(0, chart_data.shape[0]*2,2) # add lapsed time column in second
chart_data = chart_data.set_index('lasped_time')
col1.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['suctionfan[rpm]'])
chart_data['lasped_time'] = np.arange(0, chart_data.shape[0]*2,2) # add lapsed time column in second
chart_data = chart_data.set_index('lasped_time')
col2.line_chart(chart_data)