# Run the pip install command in terminal below if you don't already have the library
#pip install snscrape

# Run the below command if you don't already have Pandas
#pip install pandas

# Imports
import snscrape.modules.twitter as sntwitter #for getting data from twitter
import pandas as pd                          #for using dataframes                           
from pymongo import MongoClient              #for storing data
import datetime                              #for getting current time               
from datetime import timedelta               #for manipulating datatime
import streamlit as st                       #creating the web app


st.title("Twitter Scraper")

#Getting the user inputs
def get_input():
    col1, col2 = st.columns(2)   

    with col1:
        st.text_input("Enter the Keyword or Hashtag",key='searchTerm')
        searchTerm=st.session_state.searchTerm
        startDate = st.date_input(
                        "StartDate",
                        datetime.datetime.now()-timedelta(days=7))

    with col2:
        count = st.number_input('Count of tweets',min_value=1)
        endDate = st.date_input(
                        "EndDate",
                        datetime.datetime.now())    

    search = st.button('Search')
  
    return (searchTerm,count,startDate,endDate,search)

#Extracting the tweets
def extract_data(searchTerm,count,startDate,endDate):       
    # Setting variables to be used below
    maxTweets = count - 1
    endDate = endDate + timedelta(days=1)
    
    # Creating list to append tweet data to
    tweets_list1 = []
    
    # Using TwitterSearchScraper to scrape data and append tweets to list
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'{searchTerm} since:{startDate} until:{endDate}').get_items()):
        if i>maxTweets:
            break
        tweets_list1.append([ tweet.date, tweet.id, tweet.url,
                              tweet.content, tweet.user.username,
                              tweet.replyCount,tweet.retweetCount,
                              tweet.lang,tweet.sourceLabel,tweet.likeCount
                              ])
        
    return  pd.DataFrame(tweets_list1, 
                        columns=['Datetime', 'Tweet Id', 'URL',
                                'Content', 'Username', 'Reply Count', 
                                'Retweet Count', 'language' , 'SourceLabel', 'Like Count'
                                ])

# Storing the data frame in Mongodb
def storeData(tweets_df1):
    
    currentTime=datetime.datetime.now()
    key=f"{searchTerm} + {currentTime}"
    #connect mongodb database
    client=MongoClient()

    #Create db "twitter"
    db=client.twittert
    coll=db.tweett

    #dataframe into dict
    tweets_dict=tweets_df1.to_dict('records')

    final_dict={key:tweets_dict}
    y=coll.insert_one(final_dict)
    return y.inserted_id

#Converting dataframe into csv for download
def convert_df(df):
    return df.to_csv().encode('utf-8')

#Converting dataframe into json for download
def convert_df_json(df):
    return df.to_json(orient="index")


searchTerm,count,startDate,endDate,search=get_input()

tweets_df1=extract_data(searchTerm,count,startDate,endDate)
tweets_df1.index =tweets_df1.index + 1


# --- Initialising SessionState ---
if "load_state" not in st.session_state:
     st.session_state.load_state = False


if search or st.session_state.load_state:
    st.session_state.load_state = True    
    st.write(f"The following data is shown based on search term : {searchTerm} ")
    st.write(f"Date range : {startDate} to {endDate} limited to {count} tweets")
    st.dataframe(tweets_df1)



if st.button('Upload the data'):
    result = storeData(tweets_df1)
    if result:
        st.write('Data are inserted with id: ' , result)

col1, col2 = st.columns(2)     

with col1:     
    st.download_button(
            label="Download data as CSV",
            data=convert_df(tweets_df1),
            file_name='tweets.csv',
            mime='text/csv',
            )
        
with col2: 
    st.download_button(
            label="Download data as JSON",
            file_name="tweets.json",
            mime="application/json",
            data=convert_df_json(tweets_df1),
            )




















#json_string = convert_df_json(tweets_df1)



