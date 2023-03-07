import streamlit as st

import os
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from envyaml import EnvYAML

# from google.cloud import storage    # Uncomment to save/load the csv in/from GCS

from typing import List, Tuple

from utils.utils import float_safe_cast

st.set_page_config(layout="wide", page_title="Wine Analysis",
                   page_icon=":Wine_Glass:")

FILE_PREF = '' if 'wine_scraping' in os.getcwd() else '/tmp/'

CONF = EnvYAML(os.path.join('utils', 'config.yaml'))


@st.experimental_singleton
def load_data(name_: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load wine data and return a filtered data frame with grape list.

    Args:
        name_: Country name.

    Returns:
        Tuple of data frame and a list of unique grape categories.
    """
    data = pd.read_csv(f'wine_data_{name_}.csv',
                 sep=';', index_col=0)
    # storage_client = storage.Client()    # Uncomment to save/load the csv in/from GCS
    # bucket = storage_client.bucket('my-bucket-name')
    # blob = bucket.blob(f'wine_data_{name_}.csv')
    # blob.download_to_filename(f'{FILE_PREF}wine_data_{name_}.csv')
    # data = pd.read_csv(f'{FILE_PREF}wine_data_{name_}.csv',
    #              sep=';', index_col=0)

    data['Alcohol'] = data['Alcohol'].fillna(0).apply(
        lambda x: float_safe_cast(0 if str(x).lower() in
                                ['full', 'medium', 'light'] else x))
    data['Alcohol'] = data['Alcohol'].apply(lambda x: float(x))
    data['Vintage'] = data['Vintage'].fillna(0).apply(
        lambda x: float_safe_cast(x))
    data['Country'] = data['Country'].fillna(name_)
    
    for i, j in CONF['FILL'].items():
        data[i] = data[i].fillna(j)

    data['Grapes'] = data['Grapes'].apply(
        lambda x: str(x)[1:-1].replace("'", '').split(',')
        if str(x)[1:-1].replace("'", '').split(',')[0] != 'a' else [])

    grape_list = re.sub('[0-9%.]', '', str(', '.join(
        data['Grapes'].fillna('').apply(
        lambda x: ', '.join(x).replace(' ', '')
        if x != ['a'] or x != 'a' else None).values))).replace(
            ',,', ',').replace(' ', '').replace('"', '')
    grape_list = set(grape_list.split(','))
    
    data['Grape_Categories'] = data['Grapes'].apply(lambda x:
        ', '.join([i for i in grape_list
                   if i and i in str(x).replace(
                       ' ', '').replace('"', '')]))
    return data, grape_list

with st.sidebar:
    st.markdown('### Wine Selector')
    name_ = st.selectbox('Pick a Country:', options=CONF['COUNTRIES'])
    if name_:
        data, grape_list = load_data(name_.lower())
        image = Image.open(os.path.join(
            'img', f'wine_{name_.lower()}.jpg'))
        st.image(image, caption=f'wine {name_.lower()} alt')
        st.markdown('Use the filters to explore the data')
        st.header('Filters:')
        
        region_filter = st.multiselect(label='Select the Region',
                                    options=data['Region'].unique())
        producer_filter = st.multiselect(label='Select the Producer',
                                    options=data['Producer'].unique())
        sweetness_filter = st.multiselect(label='Select the Sweetness',
                                    options=data['Sweetness'].unique())
        wine_type_filter = st.multiselect(label='Select the Wine Type',
                                    options=data['Wine Type'].unique())
        colour_filter = st.multiselect(label='Select the Colour',
                                    options=data['Colour'].unique())
        closure_filter = st.multiselect(label='Select the Closure',
                                    options=data['Closure'].unique())
        body_filter = st.multiselect(label='Select the Body',
                                    options=data['Body'].unique())
        oak_filter = st.multiselect(label='Select the Oak',
                                    options=data['Oak'].unique())
        alcohol_filter_min, alcohol_filter_max = st.slider(
            'Select the Alcohol %',
            min_value=min(data['Alcohol']),
            max_value=max(data['Alcohol']),
            value=(min(data['Alcohol']),
                   max(data['Alcohol'])),
            step=0.01)
        vintage_filter_min, vintage_filter_max = st.slider(
            'Select the Vintage',
            min_value=min(data['Vintage']),
            max_value=max(data['Vintage']),
            value=(min(data['Vintage']),
                   max(data['Vintage'])),
            step=1.0)
        grape_filter = st.multiselect(label='Select the Grapes',
                                    options=grape_list)
        st.write('\n-------------')
        st.markdown('General Actions:')
        download_submit = st.download_button(
            'Download Raw Data', data=pd.read_csv(
                f'{FILE_PREF}wine_data_{name_}.csv', sep=';',
                index_col=0).to_csv().encode('utf-8'),
            file_name=f'wine_data_{name_}.csv')
        st.write('\n-------------')

# User Interface
st.markdown('# :wine_glass: Wine Analysis')
st.markdown(f'##### Raw Data Scraped from [here](https://www.decanter.com\
/wine-reviews/search/{name_ if name_ else "france"}/page/1/3)')

st.markdown('### Wine Graphs:')
st.markdown('\n')
st.markdown('\n')

if name_:
    if region_filter:
        data = data.loc[data['Region'].apply(
            lambda x: x in region_filter)]
    if producer_filter:
        data = data.loc[data['Producer'].apply(
            lambda x: x in producer_filter)]
    if sweetness_filter:
        data = data.loc[data['Sweetness'].apply(
            lambda x: x in sweetness_filter)]
    if wine_type_filter:
        data = data.loc[data['Wine Type'].apply(
            lambda x: x in wine_type_filter)]
    if colour_filter:
        data = data.loc[data['Colour'].apply(
            lambda x: x in colour_filter)]
    if closure_filter:
        data = data.loc[data['Closure'].apply(
            lambda x: x in closure_filter)]
    if body_filter:
        data = data.loc[data['Body'].apply(
            lambda x: x in body_filter)]
    if oak_filter:
        data = data.loc[data['Oak'].apply(
            lambda x: x in oak_filter)]
    data = data.loc[data['Alcohol'].apply(lambda x:
        x >= alcohol_filter_min and x <= alcohol_filter_max)]
    data = data.loc[data['Vintage'].apply(lambda x:
        x >= vintage_filter_min and x <= vintage_filter_max)]
    if grape_filter:
        data = data.loc[data['Grape_Categories'].apply(
            lambda x: any(y in x for y in grape_filter))]

    sweetness_col, colour_col = st.columns([3, 3])

    with sweetness_col:
        alcohol_sweetness_data = data.groupby(
            'Sweetness').mean().reset_index()
        alcohol_sweetness = px.scatter(alcohol_sweetness_data,
                                       size='Alcohol',
                                       x='Alcohol',
                                       y='Sweetness',
                                       orientation='h',
                                       title='<b>Wine Alcohol % by Sweetness</b>',
                                       template='plotly_white',
                                       color='Vintage')
        alcohol_sweetness.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=(dict(showgrid=False)))
        st.plotly_chart(alcohol_sweetness)

        closure_data_pie = data[['Title', 'Closure']].groupby(
            'Closure').count().reset_index()
        closure_pie = px.pie(closure_data_pie, values='Title',
                             names='Closure',
                             title='<b>Distribution of Wine Closures</b>')
        closure_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                        xaxis=(dict(showgrid=False)))
        st.plotly_chart(closure_pie)

    with colour_col:
        colour_region_data = data.reset_index().groupby(['Colour',
                                                         'Region']).count()
        colour_region_data = colour_region_data.reset_index()
        colour_region_data = colour_region_data.reset_index(drop=True)
        melted = pd.melt(colour_region_data, id_vars=['Colour', 'Region'],
                         value_name='Count')
        colour_region = go.Figure(data=[
            go.Bar(name='Red', x=melted[melted['Colour'] == 'Red']['Region'], 
                y=melted[melted['Colour'] == 'Red']['Count']),
            go.Bar(name='White', x=melted[melted['Colour'] == 'White']['Region'], 
                y=melted[melted['Colour'] == 'White']['Count']),
            go.Bar(name='Orange', x=melted[melted['Colour'] == 'Orange']['Region'], 
                y=melted[melted['Colour'] == 'Orange']['Count']),
            go.Bar(name='Rosé', x=melted[melted['Colour'] == 'Rosé']['Region'], 
                y=melted[melted['Colour'] == 'Rosé']['Count'])])
        colour_region.update_layout(plot_bgcolor='rgba(0,0,0,0)', barmode='stack',
                                    xaxis=(dict(showgrid=False)),
                                    title='<b>Count of Wine Colour by Region</b>')
        st.plotly_chart(colour_region)
        
        body_data_pie = data[['Title', 'Body', 'Oak']].groupby(
            ['Body', 'Oak']).count().reset_index()
        body_pie = px.pie(body_data_pie, values='Title', names='Body',
                            title='<b>Distribution of Wine Body</b>',
                            hover_data=['Oak'])
        body_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                               xaxis=(dict(showgrid=False)))
        st.plotly_chart(body_pie)

    oak_alcohol_data = data.groupby(
        ['Oak', 'Grape_Categories', 'Region']).mean().reset_index()
    oak_alcohol = px.scatter(oak_alcohol_data, size='Alcohol',
                            x='Alcohol', y='Oak', orientation='h',
                            title='<b>Wine Alcohol % by Oak</b>',
                            template='plotly_white', color='Region',
                            hover_data=['Grape_Categories', 'Vintage'])
    oak_alcohol.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=(dict(showgrid=False)),
                                autosize=False,
                                width=1400, height=600)
    st.plotly_chart(oak_alcohol)

    st.write('-----------------------')
    st.markdown('### Data Tables:')
    data_table, descr_table = st.columns([4, 1])
    
    with data_table:
        st.markdown('#### Cleaned:')
        st.dataframe(data)

    with descr_table:
        st.markdown('#### Descriptors:')
        st.dataframe(data.describe())
else:
    st.markdown('### Please select a country in the sidebar\
 (:arrow_left:) to visualize the data')
