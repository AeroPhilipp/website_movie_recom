import streamlit as st
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered", initial_sidebar_state="expanded")

import numpy as np
import pandas as pd
import requests
from streamlit_player import st_player
# for google search:
from googleapiclient.discovery import build
from params import *


if 'agree' not in st.session_state:
    st.session_state.agree = [False, False, False, False, False]
st.session_state.update_movies = False
if 'list_of_favorites' not in st.session_state:
    st.session_state.list_of_favorites = []
if 'old_list_of_favorites' not in st.session_state:
    st.session_state.old_list_of_favorites = []
if 'already_presented_list' not in st.session_state:
    st.session_state.already_presented_list = []
if 'titles_to_present' not in st.session_state:
    st.session_state.titles_to_present = []
if 'links_to_present' not in st.session_state:
    st.session_state.links_to_present = []
if 'promt' not in st.session_state:
    st.session_state.prompt = ''
if 'old_prompt' not in st.session_state:
    st.session_state.old_prompt = ''
if 'delete' not in st.session_state:
    st.session_state.delete = [False, False, False, False, False]
if 'weight_n' not in st.session_state:
    st.session_state.weight_n = 0.5
if 'old_weight_n' not in st.session_state:
    st.session_state.old_weight_n = st.session_state.weight_n
if 'text_predict_movies' not in st.session_state:
    st.session_state.text_predict_movies = False
if 'user_predict_movies' not in st.session_state:
    st.session_state.user_predict_movies = False
if 'api_return_movie_list' not in st.session_state:
    st.session_state.api_return_movie_list = []
if 'model' not in st.session_state:
    st.session_state.model = False
if 'old_model' not in st.session_state:
    st.session_state.old_model = False

#st.session_state.agree[0] = st.checkbox('add to favorites', key='agree0')


if 'show_movies' not in st.session_state:
    st.session_state.show_movies = False


def get_link(titel:str):
    my_api_key = GOOGLE_API_KEY
    my_cse_id = '4121a8a17cad24b85'#"c642a142791e24b63"
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']

    results = google_search(
        f'{titel} Official Trailer', my_api_key, my_cse_id, num=1)
    for result in results:
        return result['link']


with st.sidebar:
    # To Do implement max length of 500 characters input
    st.session_state.prompt = st.text_area('Input text (Summarise the movie):', 'Man relives the same day again and again until he learns how to interact with the world in the right way.', height=150, max_chars=1000)
    #old requests: 'Artificial intelligence is taking over'
    label = 'gsh'


    #if st.session_state.model:
    '''**Model 1 (based on Text):** Compares input text with movie summaries📝'''

    '''**Model 2 (based on Favorits):** See what users with similar favorits also liked🎯'''
    #else:
    st.session_state.model = st.toggle('Model 1 or Model 2')

    if st.button('get movies'):
        if st.session_state.old_list_of_favorites != st.session_state.list_of_favorites or st.session_state.prompt != st.session_state.old_prompt or st.session_state.weight_n != st.session_state.old_weight_n or st.session_state.model != st.session_state.old_model:
            st.session_state.old_list_of_favorites = st.session_state.list_of_favorites
            st.session_state.old_prompt = st.session_state.prompt
            st.session_state.old_weight_n = st.session_state.weight_n
            st.session_state.old_model = st.session_state.model
            if not st.session_state.model: # model 1
                st.session_state.text_predict_movies = True
                #st.session_state.update_movies = True
                st.session_state.show_movies = True
            elif len(st.session_state.list_of_favorites) > 0: # model 2 and fav list not empty
                st.session_state.user_predict_movies = True
                #st.session_state.update_movies = True
                st.session_state.show_movies = True

        if len(st.session_state.list_of_favorites) == 0 and st.session_state.model==True:
            st.warning('⚠️ Empty favorite list! Please first run Model 1 and add a movie to the favorites')
        else:
            st.session_state.update_movies = True

    # st.write('_________________')
    # if (len(st.session_state.list_of_favorites) == 0 and st.session_state.model):
    #     '''⚠️ empty favorite list! Please first run Model 1 and add a movie to the favorites'''


    #st.session_state.weight_n = st.slider('Adjust the importance of ratings', 0, 100, 50) / 100
    #st.write(st.session_state.weight_n)

# create string with fav movies
string_fav_movies = '_'.join(st.session_state.list_of_favorites)

number_of_recommendations = 20
user_input = {'prompt': st.session_state.prompt,
              'fav_list': string_fav_movies,
              'weight_n': st.session_state.weight_n,
              'weight_fav': 0.5
              }

url_text = 'https://firstworkingimage-vzyv5y24ea-ew.a.run.app/predict'
url_user = 'https://firstworkingimage-vzyv5y24ea-ew.a.run.app/alsoliked'
#url ='https://moviedocker-5re2l77u2q-ew.a.run.app/predict'
# url_text ='http://127.0.0.1:8000/predict'
# url_user ='http://127.0.0.1:8000/alsoliked'

if st.session_state.update_movies:
    st.session_state.update_movies = False
    st.session_state.already_presented_list.extend(st.session_state.titles_to_present)


    # call text api
    if st.session_state.text_predict_movies:
        st.session_state.text_predict_movies = False
        response = requests.get(url_text, params=user_input)
        data = response.json() #=> {wait: 64}
        st.session_state.api_return_movie_list = data['Our recommendation is']

    # call user api
    if st.session_state.user_predict_movies:
        st.session_state.user_predict_movies = False
        response = requests.get(url_user, params=user_input)
        data = response.json() #=> {wait: 64}
        st.session_state.api_return_movie_list = data['Our recommendation is']

    # empty list for new recommendations
    st.session_state.titles_to_present = []
    st.session_state.links_to_present = []
    i = 0
    for index, title in enumerate(st.session_state.api_return_movie_list):
        if len(st.session_state.titles_to_present) < 5 and title not in st.session_state.already_presented_list and 'youtube.com/watch' in get_link(title):
            st.session_state.titles_to_present.append(title)
            st.session_state.links_to_present.append(get_link(title))



if st.session_state.show_movies:
    for n in range(len(st.session_state.titles_to_present)):
        st_player(st.session_state.links_to_present[n], key=f'player{n}')
        #Create two columns
        col1, col2 = st.columns([0.25,0.5])
        #Add widgets to each column
        with col1:
            st.session_state.agree[n] = st.button('add to favorites', key= f'agree{n}')
        with col2:
            st.session_state.delete[n] = st.button("remove from favorites", key=f'delete{n}')
        st.write('')
        st.write('')


        if st.session_state.agree[n]:
            if st.session_state.titles_to_present[n] not in st.session_state.list_of_favorites:
                st.session_state.list_of_favorites.append(st.session_state.titles_to_present[n])
        if st.session_state.delete[n]:
            if st.session_state.titles_to_present[n] in st.session_state.list_of_favorites:
                st.session_state.list_of_favorites.remove(st.session_state.titles_to_present[n])

with st.sidebar:
    if len(st.session_state.list_of_favorites) > 0:
        st.markdown("⭐ **Favorites:**")
        #Create two columns
        #col1, col2 = st.columns([0.8,0.25])
        # Add widgets to each column
        # with col1:
        #     for j in range(len(st.session_state.list_of_favorites)):
        #         st.write(st.session_state.list_of_favorites[j])
        # with col2:
        #     for j in range(len(st.session_state.list_of_favorites)):
        #         st.session_state.delete[j] = st.button("Remove", key=f'delete{j}')
        #         if st.session_state.delete[j]:
        #             st.session_state.list_of_favorites.remove(st.session_state.list_of_favorites[j])
        for j in range(len(st.session_state.list_of_favorites)):
            st.write('  ',st.session_state.list_of_favorites[j])
        # if st.button('refine search'):
        #     st.session_state.update_movies = True
    #else:
        #'''_Add favorites to get refined\n🎯recommendations!_'''

#st.write(st.session_state.api_return_movie_list)
