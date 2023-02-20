import requests
from bs4 import BeautifulSoup
import scrape_data as LIB
import preprocess as pp
import pandas as pd
import numpy as np
import importlib
import streamlit as st
import plotly.graph_objs as go
import altair as alt
importlib.reload(LIB)
# import configs
import yaml
config = yaml.safe_load(open('scrape_ufc_stats_config.yaml'))

# Définir la largeur de la page
st.set_page_config(layout="centered")

st.title("UFC fighter comparison")

@st.cache_data(ttl=7200) # refresh ufc data every 2 hours
def get_all_fighter_detail():
    # generate list of urls for fighter details
    list_of_alphabetical_urls = LIB.generate_alphabetical_urls()
    # create empty dataframe to store all fighter details
    all_fighter_details_df = pd.DataFrame()

    # loop through list of alphabetical urls
    # with st.spinner('We are loading the latest data from ufc fighters...'):
    for url in list_of_alphabetical_urls:
            # get soup
            soup = LIB.get_soup(url)
            # parse fighter details
            fighter_details_df = LIB.parse_fighter_details(soup, config['fighter_details_column_names'])
            # concat fighter_details_df to all_fighter_details_df
            all_fighter_details_df = pd.concat([all_fighter_details_df, fighter_details_df])
    
    # Concatenate the "FIRST" and "LAST" columns into a new "Name" column
    all_fighter_details_df["Name"] = all_fighter_details_df.apply(lambda x: f"{x['FIRST']} {x['LAST']}", axis=1)
    return all_fighter_details_df

with st.spinner('Loading the latest data ...'):
    all_fighter_details_df = get_all_fighter_detail()
# define list of urls of fighters to parse
list_of_fighter_urls = list(all_fighter_details_df['URL'])
list_of_fighter_names = list(all_fighter_details_df['Name'])

col1, col2= st.columns([1,2])

with col1:
# Select fighter(s)
    selected_fighters = st.multiselect('Select fighter(s)', list_of_fighter_names)

with st.sidebar:
    st.write("_Data from http://ufcstats.com/statistics/fighters_")
    st.write("")
    st.write("")
    st.write("")
    st.write("**HEIGHT** - Meters")
    st.write("**REACH** - Meters")
    st.write("**SApM** - Significant Strikes Absorbed per Minute")
    st.write("**SLpM** - Significant Strikes Landed per Minute")
    st.write("**Str. Acc.** - Significant Striking Accuracy (%)")
    st.write("**Str. Def.** - Significant Strike Defence (the % of opponents strikes that did not land)")
    st.write("**Sub. Avg.** - Average Submissions Attempted per 15 minutes")
    st.write("**TD Acc.** - Takedown Accuracy (%)")
    st.write("**TD Avg.** - Average Takedowns Landed per 15 minutes")
    st.write("**TD Def.** - Takedown Defense (the % of opponents TD attempts that did not land)")


# Get the data for the selected fighters
fighter_data = []
for fighter_name in selected_fighters:
    idx = list_of_fighter_names.index(fighter_name)
    url = list_of_fighter_urls[idx]
    soup = LIB.get_soup(url)
    fighter_tott = LIB.parse_fighter_tott(soup)
    fighter_tott_df = LIB.organise_fighter_tott(fighter_tott, config['fighter_tott_column_names'])
    fighter_data.append(fighter_tott_df)

if fighter_data :
    df_selected_fighter = pd.concat(fighter_data).reset_index()
     # show weight category and stance
    with col2:
        st.write("")
        st.write("")
        st.write(df_selected_fighter[["FIGHTER", "WEIGHT", "HEIGHT", "REACH", "STANCE"]])
    
    # preprocessing 
    df_selected_fighter = df_selected_fighter.replace("--", "").reset_index(drop=True)
    df_selected_fighter['HEIGHT'] = df_selected_fighter['HEIGHT'].apply(pp.convert_to_meters)
    df_selected_fighter['REACH'] = df_selected_fighter['REACH'].apply(pp.inches_to_meters)
    df_selected_fighter['Str. Acc.'] = df_selected_fighter['Str. Acc.'].apply(pp.percentage_to_float)
    df_selected_fighter['Str. Def.'] = df_selected_fighter['Str. Def.'].apply(pp.percentage_to_float)
    df_selected_fighter['TD Acc.'] = df_selected_fighter['TD Acc.'].apply(pp.percentage_to_float)
    df_selected_fighter['TD Def.'] = df_selected_fighter['TD Def.'].apply(pp.percentage_to_float)
    
   # Convertir toutes les colonnes en nombres
    df_selected_fighter = df_selected_fighter.applymap(lambda x: pd.to_numeric(x, errors='ignore'))
    
    # mettre en forme la dataframe en un format de données longues
    df_melted = pd.melt(
        df_selected_fighter, 
        id_vars=['FIGHTER'], 
        value_vars=
            [
                'HEIGHT', 
                'REACH',
                'SLpM',
                'Str. Acc.',
                'SApM',
                'Str. Def.',
                'TD Avg.',
                'TD Acc.',
                'TD Def.',
                'Sub. Avg.'
            ]
    )
    
    # créer le graphique avec Altair
    chart = alt.Chart(df_melted).mark_bar().encode(
        y=alt.Y('FIGHTER:N', axis=alt.Axis(title='')),
        x=alt.X('value:Q', axis=alt.Axis(title='')),
        color=alt.Color('FIGHTER:N', legend=alt.Legend(title='')),
        row=alt.Column('variable:N', header=alt.Header(title='', titleOrient='top', labelOrient='top', labelAngle=0))
    )
    
    # chart
    st.altair_chart(chart, use_container_width=True)
