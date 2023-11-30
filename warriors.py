from datetime import date

import streamlit as st

# For the Lottie file GSW Logo
from streamlit_lottie import st_lottie
import json

# For the DuckDuckGo search results
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import DuckDuckGoSearchResults

# For the LLM to perform summarization
import cohere
from cohere.responses.classify import Example

# A helper function to get rid of the "helpful" message from Cohere at the end of summarization
def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

co = cohere.Client(st.secrets["cohere_api"])

# For local lottie file
lottie_GSW = "C:\\Users\\Kingpin\\AAARex\\code\\streamlit\\PycharmProjects\\warriors\\GSW_Lottie.json"
with open(lottie_GSW, "r") as f:
    gsw_lottie_data = json.load(f)

# Setting up the page
st.set_page_config(page_title = "GSW LLM Superfan Page", page_icon = ":tada:", layout = "wide")

# ---- HEADER SECTION ----
with st.container():
    left_column, right_column = st.columns(2)

    with left_column:
        st.title("Rex's Golden State Warriors Fan Page!")
        st.write("Driven by Large Language Models")

    with right_column:
        st_lottie(gsw_lottie_data, height=200, key="coding")

# ---- Warriors in two columns ----
with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("What's new with the Warriors?")
        st.write("##")

        with st.spinner("Loading the latest news..."):

            wrapper = DuckDuckGoSearchAPIWrapper(max_results=10)
            search = DuckDuckGoSearchResults(api_wrapper=wrapper)

            today = date.today()
            formatted_date = today.strftime('%B %d, %Y')
            print(formatted_date)

            rawInfo = search.run(f"Golden State Warriors news as of today {formatted_date}")
            #rawInfo = search.run("Food truck business latest strategies")
            sum_response = co.summarize(text = rawInfo,
                                length='long',
                                format='bullets',
                                model='summarize-xlarge',
                                additional_command='',
                                temperature=1.0,)
            st.write(remove_last_line_from_string(sum_response.summary))

    with right_column:

        import random
        import requests
        from bs4 import BeautifulSoup
        URL = "https://www.goldenstateofmind.com/"
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

with st.container():

    with st.spinner("Let's go get a sentiment..."):

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
        if (rawSentiment == 'negative'):
            sentimentColor = "red"
        else:
            sentimentColor = "blue"
        st.header("Overall sentiment of the Warriors is currently trending " +
                 f":{sentimentColor}[{rawSentiment}].")

with st.container():
    st.write("---")

    # Let's map the Warriors stadium
    st.header("Go see the Warriors play at Chase Center in Mission Bay!")
    import pandas as pd
    import numpy as np

    df = pd.DataFrame(
        {
            "lat": [37.768],
            "lon": [-122.388]
        }
    )
    #print(df)
    st.map(df, zoom = 12, size = 200, color =  '#FFC72C')

