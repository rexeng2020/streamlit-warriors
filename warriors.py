from datetime import date

import streamlit as st

# For the Lottie file GSW Logo
from streamlit_lottie import st_lottie
import json

# For the DuckDuckGo search results
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

# For the LLM to perform summarization
import cohere
from cohere.responses.classify import Example

# A helper function to get rid of the "helpful" message from Cohere at the end of summarization
def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

co = cohere.Client(st.secrets["cohere_api"])

# For local lottie file
lottie_GSW = "GSW_Lottie.json"
with open(lottie_GSW, "r") as f:
    gsw_lottie_data = json.load(f)

# Setting up the page configuration: it MUST BE the first st call on the page!
st.set_page_config(page_title = "GSW LLM Superfan Page", page_icon = ":tada:", layout = "wide")

# Get current time and convert it to a good format
today = date.today()
formatted_date = today.strftime('%B %d, %Y')
print(formatted_date)

# If the timestamps file does not yet exist, then app is running the first time
import os
firstTime = False
getNewData = False
if os.path.isfile("timestamps.csv"):
    print("Running app the nth time")
else:
    print("Running app for the first time")
    firstTime = True
    getNewData = True

# Let's figure out if we should get new data if its not the first time the app is running!
import datetime as dt
from datetime import datetime
if not firstTime:
    with open('timestamps.csv', "r", encoding="utf-8", errors="ignore") as readableTimeFile:
        strLastStamp = readableTimeFile.readlines()[-1]
        print(strLastStamp)
        lastStamp = datetime.strptime(strLastStamp.strip(), "%Y-%m-%d %H:%M:%S.%f")
        print(lastStamp)
        if abs(datetime.now() - lastStamp) > dt.timedelta(hours = 6):
           getNewData = True
        readableTimeFile.close()

# Open or create create the timestamps file. It will not yet exist if firstTime
timeFile = open('timestamps.csv', 'a', newline='')

# Create the cache files if they don't already exist
summaryFile = open('newestSummary.txt', 'a', newline='')
summaryFile.close()
sentimentFile = open('newestSentiment.txt', 'a', newline='')
sentimentFile.close()

# Write the current timestamp into the timestamps file, but only if getNewData is True!
# That way, we only keep timestamps of when we retrieve new data.
import csv
if getNewData:
    file_writer = csv.writer(timeFile)
    # storing current date and time
    current_date_time = datetime.now()
    file_writer.writerow([current_date_time])
    timeFile.close()

# ---- HEADER SECTION ----
with st.container():
    left_column, right_column = st.columns(2)

    with left_column:
        st.title("My Golden State Warriors Fan Page!")
        st.write("Driven by Large Language Models")
        st.write("Made by [Rex Eng](https://www.linkedin.com/in/rexeng/)")

    with right_column:
        st_lottie(gsw_lottie_data, height=200, key="coding")

# ---- Warriors in two columns ----
with st.container():

    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:

        st.header(f"Latest News as of {formatted_date}")
        st.write("##")

        if firstTime and getNewData:
            print("First time running app: get new data!")
        elif getNewData:
            print("It has been more than 1 hour: get new data!")
        else:
            print("It has been less than 1 hour, so do not fetch new data.")

        with st.spinner("Getting the latest news..."):

            try:
                if getNewData:
                    wrapper = DuckDuckGoSearchAPIWrapper(max_results=10)
                    search = DuckDuckGoSearchResults(api_wrapper=wrapper)

                    rawInfo = search.run(f"Golden State Warriors latest news as of today {formatted_date}")
                    sum_response = co.summarize(text = rawInfo,
                                        length='long',
                                        format='bullets',
                                        model='summarize-xlarge',
                                        additional_command='',
                                        temperature=1.0,)
                    cleanedSummary = remove_last_line_from_string(sum_response.summary)
                    st.write(cleanedSummary)

                    # Cache the summary!
                    file = open("newestSummary.txt", "w")
                    file.seek(0)
                    file.write(cleanedSummary)
                    file.truncate()
                    file.close()
                else:
                    # Read the cached summary!
                    file = open("newestSummary.txt", "r")
                    fileContent = file.read()
                    file.close()
                    st.write(fileContent)
            except Exception as e:
                print("Rex: the exception is: ")
                print(e)
            finally:
                pass
            
        with st.spinner("Let's go get a sentiment..."):

            rawSentiment = ""

            if getNewData:
                examples=[
                  Example("The order came 5 days early", "positive review"),
                  Example("The item exceeded my expectations", "positive review"),
                  Example("I ordered more for my friends", "positive review"),
                  Example("I would buy this again", "positive review"),
                  Example("I would recommend this to others", "positive review"),
                  Example("The package was damaged", "negative review"),
                  Example("The order is 5 days late", "negative review"),
                  Example("The order was incorrect", "negative review"),
                  Example("I want to return my item", "negative review"),
                  Example("The item's material feels low quality", "negative review"),
                  Example("The product was okay", "neutral review"),
                  Example("I received five items in total", "neutral review"),
                  Example("I bought it from the website", "neutral review"),
                  Example("I used the product this morning", "neutral review"),
                  Example("The product arrived yesterday", "neutral review")
                ]

                inputs=[
                  sum_response.summary
                ]

                sentiment_response = co.classify(
                  inputs=inputs,
                  examples=examples,
                )
                # The slice at the end gets rid of the word "review"
                rawSentiment = sentiment_response.classifications[0].prediction[:-7]
                # Cache the sentiment!
                file = open("newestSentiment.txt", "w")
                file.seek(0)
                file.write(rawSentiment)
                file.truncate()
                file.close()
            else:
                # Read the cached sentiment!
                file = open("newestSentiment.txt", "r")
                fileContent = file.read()
                file.close()
                rawSentiment = fileContent

            if (rawSentiment == 'negative'):
                sentimentColor = "red"
            else:
                sentimentColor = "blue"
            st.header("Warriors sentiment is trending " +
                     f":{sentimentColor}[{rawSentiment}].")

    with right_column:

        import random
        import requests
        from bs4 import BeautifulSoup
        URL = st.secrets["photos_source"]
        r = requests.get(URL)

        soup = BeautifulSoup(r.content, features = 'lxml')  # If this line causes an error, run 'pip install html5lib' or install html5lib
        images = soup.select('div img')
        images_url = images[random.randint(5,8)]['src']
        img_data = requests.get(images_url).content
        with open('test.jpg', 'wb') as handler:
            handler.write(img_data)

        from PIL import Image
        image = Image.open('test.jpg')
        st.image(image, caption='')
