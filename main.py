import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import warnings
warnings.simplefilter('ignore')
from googleapiclient.discovery import build
import time
import requests
from matplotlib.backends.backend_agg import RendererAgg
from func import get_video_list,get_video_details
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
_lock = RendererAgg.lock
import config



st.set_page_config(page_title='Youtube Channel Analysis', 
                   page_icon='chart_with_upwards_trend',
                   layout="wide")


st.write("""
    ### Youtube Channel Analysis 
    """)

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    
    return response['items']

CHANNEL_ID = st.text_area('Insert a Youtube Channel ID',"UC0C-w0YjGpqDXGB8IHb662A")
st.write("""
##### You can convert channel name to channel ID in this website.
[[Convert to channel id](https://commentpicker.com/youtube-channel-id.php)]
""")
stats = get_channel_stats(youtube,CHANNEL_ID)

st.write('')


padding1,row1_1, padding2,row1_2,padding3,row1_3,padding4 =st.columns((.15, 1, .3, 2, .00000001, 3, 0.15))

with row1_1, _lock:

    youtube_stats = stats[0]['statistics']
    dp_channel = stats[0]['snippet']['thumbnails']['high']['url']
    st.subheader('Channel Info')
    st.image(dp_channel,width=200)
    

with row1_2, _lock:
    st.subheader(' ')
    st.text(' ')
    st.text(' ')
    st.text(f"Channel Name : {stats[0]['snippet']['title']}")
    st.text(f"Subscribers :{stats[0]['statistics']['subscriberCount']}")
    st.text(f"Total Views: {stats[0]['statistics']['viewCount']}")
    st.text( f"Total Videos: {stats[0]['statistics']['videoCount']}")
subscriberCount = int(stats[0]['statistics']['subscriberCount'])   
channel_stats = get_channel_stats(youtube, CHANNEL_ID)
upload_id = channel_stats[0]['contentDetails']['relatedPlaylists']['uploads']
video_list = get_video_list(youtube, upload_id)
video_data = get_video_details(youtube, video_list)

# save to dataframe
df=pd.DataFrame(video_data)
df['description'] = df['description'].str[:100]
df['title_length'] = df['title'].str.len()
df["view_count"] = pd.to_numeric(df["view_count"])
df["like_count"] = pd.to_numeric(df["like_count"])
#df["dislike_count"] = pd.to_numeric(df["dislike_count"])
df["comment_count"] = pd.to_numeric(df["comment_count"])
# reaction used later add up likes + dislikes + comments
df["reactions"] = df["like_count"] + df["comment_count"]
df['published'] = pd.to_datetime(df['published'], infer_datetime_format=True, errors='coerce')
df['year'] = pd.to_datetime(df['published']).dt.strftime('%Y')
df['month'] = pd.to_datetime(df['published']).dt.strftime('%b')
df['day'] = pd.to_datetime(df['published']).dt.strftime('%d')
df['time'] = pd.to_datetime(df['published']).dt.strftime('%H:%M:%S')

start = df.published.min()
end = df.published.max()
start_date = st.date_input('Start date', start)
end_date = st.date_input('End date', end)
df1 = df.loc[(df['published'].dt.date >= start_date) & (df['published'].dt.date <= end_date) ]
 



gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
gridOptions = gb.build()

AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True)

year_grup_views = df.groupby('year').view_count.agg(["sum","mean","min","max","count","median"])
year_grup = df.groupby('year').view_count.agg(["sum","mean","min","max","count","median"])

with row1_3, _lock:
   
    st.subheader('Video Log')
    year_grup= df.groupby('year')['view_count','like_count','comment_count'].agg(["sum","mean","min","max","count"])
    st.dataframe(year_grup.style.format().highlight_max(color='lightgreen').highlight_min(color='#cd4f39'),width=10000,height=700)

row3_1,row3_2 = st.columns((1,1))

with row3_1,_lock:
    fig = px.bar(year_grup_views, y='sum')
    fig.update_layout(
    title='Number of Views per Year', 
    xaxis = dict(rangeslider = dict(visible=True, thickness=0.05)), 
    yaxis = dict(), 
    paper_bgcolor='#FFFFFF', 
    showlegend=True)
    
    st.plotly_chart(fig)

with row3_2,_lock:
    fig = px.bar(year_grup_views, y='mean')
    fig.update_layout(
    title='Average Views per Year', 
    xaxis = dict(rangeslider = dict(visible=True, thickness=0.05)), 
    yaxis = dict(), 
    paper_bgcolor='#FFFFFF', 
    showlegend=True)
    
    st.plotly_chart(fig)
   
fig = make_subplots(rows=1, cols=2,specs=[[{"type": "pie"}, {"type": "pie"}]])
pie_vars = ['Reacters','Neutral'];
pie_values = [df1['reactions'].sum(),df1['view_count'].sum()-(df1['reactions'].sum())]
fig.add_trace(go.Pie(values=pie_values, labels=pie_vars),1,1)

pie_vars1 = ['Likers','Commenters'];
pie_values1 = [df1['like_count'].sum(),df1['comment_count'].sum()]
fig.add_trace(go.Pie(values=pie_values1, labels=pie_vars1),1,2)

fig.update_layout(title_text='People React on Video',height=400, width=1200)
st.plotly_chart(fig)



fig = make_subplots(rows=1, cols=2)
bar_vars = ['Views','Subscribers','Likes','Comments']
bar_values = [df1.describe()['view_count']['mean'],subscriberCount,df.describe()['like_count']['mean'],df.describe()['comment_count']['mean']]
fig.add_trace(go.Bar(x=bar_vars, y=bar_values),
              1, 1)
bar_vars1 = ['Views','Likes','Comments']
bar_values1 = [df1.describe()['view_count']['mean'],df.describe()['like_count']['mean'],df.describe()['comment_count']['mean']]
fig.add_trace(go.Bar(x=bar_vars1, y=bar_values1),
              1, 2)
fig.update_layout(
title='Comparasion',height=400, width=1200)
st.plotly_chart(fig)


fig_view = plt.figure(figsize=(10, 4))
plot = sns.barplot(x="view_count", y="title", data=df1.nlargest(10, 'view_count'), palette="bright")
plot.set(xlabel='Views', ylabel='')
plot.set_title('Most Viewed Videos')
st.pyplot(fig_view)

fig_like = plt.figure(figsize=(10, 4))
plot = sns.barplot(x="like_count", y="title", data=df1.nlargest(10, 'like_count'), palette="bright")
plot.set(xlabel='Likes', ylabel='')
plot.set_title('Most Liked Videos')
st.pyplot(fig_like)




st.write("""
#### You can find this project on GitHub.
[[Source Code](https://github.com/Aloyfarera/Youtube-Analysis-Streamlit)]
""")



