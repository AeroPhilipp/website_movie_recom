import streamlit as st
import numpy as np
import pandas as pd
import requests
from streamlit_player import st_player
# for google search:
from googleapiclient.discovery import build
from params import *


st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="expanded", menu_items=None)

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
if 'predict_movies' not in st.session_state:
    st.session_state.predict_movies = False
if 'api_return_movie_list' not in st.session_state:
    st.session_state.api_return_movie_list = []

#st.session_state.agree[0] = st.checkbox('add to favorites', key='agree0')


if 'show_movies' not in st.session_state:
    st.session_state.show_movies = False


def get_link(titel:str):
    my_api_key = GOOGLE_API_KEY
    my_cse_id = "c642a142791e24b63"
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']

    results = google_search(
        f'{titel} Trailer', my_api_key, my_cse_id, num=1)
    for result in results:
        return result['link']


with st.sidebar:
    # To Do implement max length of 500 characters input
    st.session_state.prompt = st.text_area('Summarise the movie:', 'Drug addict trying to get his life back', height=170, max_chars=1000)
    if st.button('generate recommendations'):
        if st.session_state.old_list_of_favorites != st.session_state.list_of_favorites or st.session_state.prompt != st.session_state.old_prompt or st.session_state.weight_n != st.session_state.old_weight_n:
            st.session_state.old_list_of_favorites = st.session_state.list_of_favorites
            st.session_state.old_prompt = st.session_state.prompt
            st.session_state.old_weight_n = st.session_state.weight_n
            st.session_state.predict_movies = True
        st.session_state.update_movies = True
        st.session_state.show_movies = True
    st.write('')

    st.session_state.weight_n = st.slider('Adjust the importance of ratings', 0, 100, 50) / 100
    #st.write(st.session_state.weight_n)

# create string with fav movies
string_fav_movies = '_'.join(st.session_state.list_of_favorites)

number_of_recommendations = 20
user_input = {'prompt': st.session_state.prompt,
              'fav_list': string_fav_movies,
              'weight_n': st.session_state.weight_n,
              'weight_fav': 0.5
              }

#url = 'https://firstworkingimage-qgokkfvvpq-ew.a.run.app/predict'
#url ='https://moviedocker-5re2l77u2q-ew.a.run.app/predict'
url ='http://127.0.0.1:8000/predict'

if st.session_state.update_movies:
    st.session_state.update_movies = False
    st.session_state.already_presented_list.extend(st.session_state.titles_to_present)

    # call api
    if st.session_state.predict_movies:
        st.session_state.predict_movies = False
        response = requests.get(url, params=user_input)
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
        st.write('')
        st.write('')
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


#st.write(st.session_state.api_return_movie_list)
