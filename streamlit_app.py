import numpy as np
import pandas as pd

import streamlit as st
import hashlib

import gdown
from datetime import date, datetime, time, timedelta
import re
import pytz

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

# download a google drive spreadsheet file
def get_gdrive_spreadsheet(doc_id, sheet_id, file_name):
    sheet_url = f'https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}'
    df = pd.read_csv(sheet_url)
    #df.to_csv(file_name)
    return df

# download a google drive file
#@st.cache(suppress_st_warning=True)
def get_gdrive_file(_id, file_name):
    print("loading gdrive file ID: ",_id)
    gdown.download('https://drive.google.com/uc?id=' + _id, file_name,quiet=True)
    
    

##### BEGIN OF THE CODE

# use full width of the page
st.set_page_config(layout="wide")

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
#start_hour = col1.slider(label='Select hour past midnight', min_value=0, max_value=22, step=2, value=2)
set_time = col1.slider('Set Time', value=time(2,0,0),
                              min_value=time(0, 0, 0),
                              max_value=time(23, 0, 0),
                              step=timedelta(hours=1),
                              format='HH:mm')
start_hour = set_time.hour

# work out the number of samples to load for the selected portion of time
start_sample = int(start_hour * 3600) # start samples
number_samples = 3600 # number of samples equivament to 1h 

# select date
new_date = col2.date_input('Pick a Day', date(2021,11,1))

# setup a 4 column layout
#col1, col2 = st.columns(2)

# data info text
txtbox3 = col3.empty()
txtbox4 = col4.empty()
#txtbox3.text('Showing 3600 samples worth of data from ' + str(start_hour) + ':00')

# Define local file path (only used with a local csv database)
#B4B_MSG_FILE_LOC  = ('../logs/SystemMea_dp_' + new_date.strftime("%Y_%m_%d") + '.zip')
#KYMA_MSG_FILE_LOC = ('../logs/Kyma/BalueiroSegundo ' + new_date.strftime("%Y-%m-%d") + '.zip')

# search for Google Drive ID for the 3 files to download

# Bound4Blue Alarm File
file_name = 'alarms_' + new_date.strftime("%Y_%m_%d") + '.zip'
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
file_name = 'message_' + new_date.strftime("%Y_%m_%d") + '.zip'
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
    msg = 'WARNING. DATA FOR ' + new_date.strftime("%Y-%m-%d") + ' IS NOT AVAILABLE.'
    msg = '<p style="color:Red;">'+msg+'</p>'
    txtbox4.markdown(msg, unsafe_allow_html=True)
    txtbox4.markdown(msg+'Loading last available data.', unsafe_allow_html=True)

    print('ERROR loading csv files')
else:
    txtbox4.text('REMOTE DATA LOADED SUCCESSFULLY.')

# setup a 2 column layout
col1, col2 = st.columns(2)

# show a partial data table starting from the selected time
if col1.checkbox('Show Raw Data Table', value = True):
    data = load_data('tmp/b4b_msg_db.zip', start_sample, number_samples) # load selected portion of data 
    col1.text('Showing 1h worth of data')
    col1.dataframe(data,height=500) # show table

# show a map with lat/long vessel position
if col2.checkbox('Show Map', value = True):
    # load lat/long data from Kyma files
    if True:
        start_sample = 0 # start samples
        number_samples = 3600*24 # number of samples equivament to 24h 
        data = load_data('tmp/b4b_msg_db.zip',start_sample,number_samples)
        data.rename({'lat_deg':'lat','long_deg':'lon'}, axis='columns',inplace=True)
        col2.text('Showing 24h worth of vessel navigation data (B4B data)')
        col2.map(data)
        #col2.dataframe(data,height=500) # show table

    # load lat/long data from Kyma files
    if False:
        start_sample = int(start_hour/15 * 3600) # start samples
        number_samples = 3600*24/15 # number of samples equivament to 24sh 
        data = load_data('tmp/kyma_msg_db.zip',start_sample,number_samples)
        data.rename({'latitude (text)':'lat','longitude (text)':'lon'}, axis='columns',inplace=True)
        data['lat'] = data['lat'].apply(dms2dd)
        data['lon'] = data['lon'].apply(dms2dd)
        col2.text('Showing 24h worth of vessel navigation data (KYMA data)')
        col2.map(data)
        #col2.dataframe(data,height=500) # show table


# load a portion, just 2h, of the data starting from the slider time
start_sample = int(start_hour * 3600) # start samples
number_samples = 3600 # number of samples equivament to 1h 
data = load_data('tmp/b4b_msg_db.zip', start_sample, number_samples) # load selected portion of data 

# PLOT some data
chart_data = pd.DataFrame(data,columns=['awa_deg','esail_pos_deg','sail_pos_target_deg','sail_pos_command_deg'])
col1.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['aws_kn','suction_speed_command_rpm','suction_speed_target_rpm','suction_speed_estimated_rpm'])
col2.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['power_cons_kw', 'mean_current_a', 'current_state'])
col1.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['aoa_deg','auto_mode_status','current_state'])
col2.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['heel_deg', 'sog_kn'])
col1.line_chart(chart_data)

# PLOT some data
chart_data = pd.DataFrame(data,columns=['skin_press1_mbar', 'skin_press2_mbar', 'skin_press3_mbar', 'skin_press4_mbar', 'skin_press5_mbar', 'skin_press6_mbar', 'skin_press7_mbar'])
col2.line_chart(chart_data)
