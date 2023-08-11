import pandas as pd
import streamlit as st
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo
from func import get_video_list,get_video_details,get_channel_stats,convert_df_to_csv
import streamlit as st
import plotly.express as px
from googleapiclient.discovery import build
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.metric_cards import style_metric_cards
from markdownlit import mdlit
import textwrap

st.set_page_config(page_title='Youtube Channel Analysis', 
                   page_icon='chart_with_upwards_trend',
                   layout="wide")
st.write("""
    ### Youtube Channel Analysis 
    """)
#######################################################################################################3

CHANNEL_ID = st.text_input("Enter some Youtube Channel ID 👇", value="UCX6OQ3DkcsbYNE6H8uQQuVA")
youtube = build('youtube', 'v3', developerKey='AIzaSyAwHiDjI46hfBl-ieeMTIeDOL_Qdv2ePrg')
stats = get_channel_stats(youtube,CHANNEL_ID)


st.write("""
[[Convert channel name to channel ID](https://commentpicker.com/youtube-channel-id.php)]
""")
st.warning('This app uses the free YouTube API, which has a daily limit of 10,000 requests', icon="⚠️")
placeholder = st.empty()
channel_name= stats[0]['snippet']['title']
subscribers= int(stats[0]['statistics']['subscriberCount'])
total_views= int(stats[0]['statistics']['viewCount'])
total_videos = int(stats[0]['statistics']['videoCount'])
subscriberCount = int(stats[0]['statistics']['subscriberCount'])   
channel_stats = get_channel_stats(youtube, CHANNEL_ID)
upload_id = channel_stats[0]['contentDetails']['relatedPlaylists']['uploads']
video_list = get_video_list(youtube, upload_id)
video_data = get_video_details(youtube, video_list)
###########################################################################################
# save to dataframe
df=pd.DataFrame(video_data)
df['description'] = df['description'].str[:100]
df['title_length'] = df['title'].str.len()
df["view_count"] = pd.to_numeric(df["view_count"])
df["like_count"] = pd.to_numeric(df["like_count"])
df["comment_count"] = pd.to_numeric(df["comment_count"])
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
with placeholder.container():
        # create three columns
        st.subheader('Channel Info')
        kpi1, kpi2, kpi3, kpi4= st.columns(4)

        # fill in those three columns with respective metrics or KPIs 
        youtube_stats = stats[0]['statistics']
        dp_channel = stats[0]['snippet']['thumbnails']['high']['url']
        st.image(dp_channel,width=100)
        kpi1.metric(label="Channel Name 📺",value= channel_name)
        kpi2.metric(label="Total Subscibers 🏆",value='{:,.0f}'.format(subscribers))
        kpi3.metric(label="Total Views 👀",value='{:,.0f}'.format(total_views))
        kpi4.metric(label="Total Videos 🎥",value='{:,.0f}'.format(total_videos))
        style_metric_cards(border_left_color= "#F30E0E")#using streamlit extras metric cards

#show dataframe
st.data_editor(
    df1,
    column_config={
        "reactions": st.column_config.ProgressColumn(
            "reactions",
            help="Reactions",
            format="%f",
            min_value=0,
            max_value=max(df1['reactions']),
        ),
    },
    hide_index=True,
)
st.download_button(
  label="Download data as CSV",
  data=convert_df_to_csv(df1),
  file_name=f'{channel_name}.csv',
  mime='text/csv',
)
year_grup_views = df1.groupby('year').view_count.agg(["sum","mean","min","max","count","median"])
year_grup = df1.groupby('year').view_count.agg(["sum","mean","min","max","count","median"])
fig_like = px.bar(
                df.nlargest(10, 'like_count'),
                x='like_count',
                y='title',
                orientation='h',  # Horizontal orientation
                title='Top 10 Most Liked Videos',
                text='like_count',  # Display like counts on bars
                labels={'like_count': 'Likes'}
            )
fig_like.update_traces(texttemplate='%{text:,}',marker_color='red')
# Customize the layout for the like chart
fig_like.update_layout(
    xaxis_title='Likes',
    yaxis_categoryorder='total ascending',
    width = 550
    )

# Create a Plotly bar chart for the most viewed videos
fig_view = px.bar(
    df.nlargest(10, 'view_count'),
    x='view_count',
    y='title',
    orientation='h',  # Horizontal orientation
    title='Top 10 Most Viewed Videos',
    text='view_count',  # Display view counts on bars
    labels={'view_count': 'Views'}
)
fig_view.update_traces(texttemplate='%{text:,}',marker_color='red')
# Customize the layout for the like chart
fig_view.update_layout(
    xaxis_title='Views',
    yaxis_categoryorder='total ascending',
    width = 550
    )
col1, col2 = st.columns([50, 50])
with col1:
    with st.expander("Top 10 Most Viewed Videos"):
            st.plotly_chart(fig_view)
with col2:
    with st.expander("Top 10 Most Liked Videos"):
            st.plotly_chart(fig_like)

     

fig_mview = px.line(year_grup_views, y='sum',markers = True, color_discrete_sequence=['red'])
fig_mview.update_layout(
title='Number of Views per Year',  
showlegend=True,
width = 550)


fig_aview = px.line(year_grup_views, y='mean',markers = True, color_discrete_sequence=['red'])
fig_aview.update_layout(
title='Average Views per Year', 
paper_bgcolor='#FFFFFF', 
showlegend=True,
width = 550)


col_most_v, col_most_l = st.columns([50, 50])
with col_most_v:
    with st.expander("Number Views per Year"):
            st.plotly_chart(fig_mview)
with col_most_l:
    with st.expander("Average Views per Year"):
            st.plotly_chart(fig_aview)


#soon..
# bar_vars = ['Likes', 'Comments']
# bar_values = [df1['like_count'].mean(), df1['comment_count'].mean()]

# fig_pie_comparasion1 = px.pie(values=bar_values, names=bar_vars, hole=.4)
# fig_pie_comparasion1.update_layout(
#     title='Metric Comparison',
#     xaxis_title='Metrics',
#     yaxis_title='Average Values',
#     height=400,
#     showlegend=False  # Hide legend
# )

# st.plotly_chart(fig_pie_comparasion1)
