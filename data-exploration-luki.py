import streamlit as st
from pathlib import Path
import os
import pandas as pd
import numpy as np

import altair as alt
from io import BytesIO

# temporarily saves the file
@st.cache_data
def save_uploadedfile(uploaded_file, path: str):
    with open(os.path.join(path, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())



path = Path(__file__).parent.resolve()

st.header("Masterarbeit Analyse - Disco Luki \n Drag and drop your .xlsx file and explore your data:")

uploaded_data_file = st.file_uploader("Upload your Excel file with the combined analysis output", type=["xlsx"],
                                          accept_multiple_files=False)

if uploaded_data_file is not None:

    save_uploadedfile(uploaded_file=uploaded_data_file, path=path)
    # file_extension = uploaded_data_file.name.split(".")[-1]
    file_name_data = uploaded_data_file.name.split(".")[0] + "." + uploaded_data_file.name.split(".")[1]

    st.write("Data File name", file_name_data)

    path_to_data_file = str(path) + "/" + file_name_data


    sheets_dict = pd.read_excel(path_to_data_file,
                                sheet_name=['Tabelle1_alt', 'Tabelle2_neu', 'Datasheet'])
    
    
    table_old = sheets_dict.get("Tabelle1_alt")
    table_new = sheets_dict.get('Tabelle2_neu')
    datasheet = sheets_dict.get("Datasheet")

    st.header("Data Visualisation:")

    #st.write(list(table_new.columns))
    st.write(" Quick preview on dataset: \n", table_new.head())

    # Number of countries conducting studies over the years
    number_countries_per_year = table_new[["year", "country"]].groupby('year').count()
    number_countries_per_year = number_countries_per_year.reset_index()
    number_countries_per_year['year'] = number_countries_per_year['year'].astype(int) 
    st.write(number_countries_per_year)

    country_year_visual = alt.Chart(number_countries_per_year).mark_bar().encode(
        x = 'year',
        y = 'country'
    ).properties(
        title = "Number of studies conducted per year"
    ).interactive()

    st.altair_chart(country_year_visual, use_container_width=True)

    # Number of studies per Country 
    number_studies_per_country = table_new[["year", "country"]].groupby('country').count()
    number_studies_per_country = number_studies_per_country.reset_index()
    number_studies_per_country['year'] = number_studies_per_country['year'].astype(int) 
    st.write(number_studies_per_country)

    country_studies_visual = alt.Chart(number_studies_per_country).mark_bar().encode(
        x = 'country',
        y = 'year'
    ).properties(
        title = "Number of studies per country"
    ).interactive()

    st.altair_chart(country_studies_visual, use_container_width=True)

    # TODO - check how these two categorical variables should be plotted

    # Trial type (nur column) und subs_cat

    trial_type_subs_cat = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    x='subs_cat',
    y='trial_type',
    #size='gdl_subs',
    color='subs_cat1'
    ).properties(
        title = "Categorization of substrate (organic, mineral, …) per trial type"
    ).interactive()

    st.altair_chart(trial_type_subs_cat, use_container_width=True)

    ########################## need to ask about this



    # Trial type (nur column) und ox_eff_avg
    trial_type_ox_eff_avg = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    x='ox_eff_avg',
    y='trial_type',
    #size='gdl_subs',
    color='subs_cat1'
    ).properties(
        title = "Percentage of 'ox_avg' from 'load_avg' per trial type"
    ).interactive()

    st.altair_chart(trial_type_ox_eff_avg, use_container_width=True)



    # Trial type (nur column) und load_avg und ox_avg (3 variablen möglich?)

    load_ox_per_trial = alt.Chart(table_new).mark_circle(size = 60).encode(
        x = "load_avg",
        y = "ox_avg",
        color = "trial_type",
        tooltip = ["country", "year", "subs_cat", "pH", "ox_avg_type"]
    ).properties(
        title = "Average influx of ch4 to subtrate vs. oxidised ch4 (trial type color-coded)"
    ).interactive()
    load_ox_per_trial.configure_header(
        titleColor='black',
        titleFontSize=14,
    )

    st.altair_chart(load_ox_per_trial, use_container_width=True)

    # Trial type (nur column) und subs_cm
        
    trial_type_subs_cm = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    x='subs_cm',
    y='trial_type',
    #size='gdl_subs',
    color='subs_cat1'
    ).properties(
        title = "Height of methane oxidation layer per trial type"
    ).interactive()

    st.altair_chart(trial_type_subs_cm, use_container_width=True)

    st.header("Self-chosen visuals:")

    col1, col2 = st.columns(2, gap="medium")

    with col1:

        options_one = table_new.columns
        var1 = st.selectbox("Please select the Measurement variable you want to visualize on the X-axis",
                        options = options_one)
        var1_series = table_new[var1]

    with col2:

        options_two = table_new.columns
        var2 = st.selectbox("Please select the Stress variables you want to visualize on the Y-axis",
                        options=options_two)
        var2_series = table_new[var2]

    #try:

        #st.write(Patient_one_time)

    #    if var1 == "ID":
    #        combined_plot = alt.Chart(table_new).mark_circle(size=60).encode(
    #            x=alt.X(var1, sort = ['Pat.1, Pat.2']),
    #            y=var2,
    #            tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg",
    #                        "ox_eff_avg"]
    #        ).interactive()

        #elif var2 == "ID":
        #    combined_plot = alt.Chart(Patient_one_time).mark_circle(size=60).encode(
        #        x = var1,
        #        y=alt.Y(var2, sort = ['Pat.1, Pat.2']),
        #        tooltip=["ID", "Gender", "STAI-T/T-Werte", "PostOPFrage", "Sedierung erhalten", "Mepivacain 1%/ml",
        #                 "NRS max"]
        #    ).interactive()

    #    else:
    combined_plot = alt.Chart(table_new).mark_circle(size = 60).encode(
        x = var1,
        y = var2,
        tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
    ).interactive()

    st.altair_chart(combined_plot, use_container_width=True)

    add_color_var = st.checkbox("Add color indicator variable: ")

    if add_color_var:
        options_three = table_new.columns

        var3 = st.selectbox("Select variable for coloring:",
                            options=options_three)
        var3_series = table_new[var3]

        combined_plot_data = pd.concat([var1_series, var2_series, var3_series], axis=1)

        combined_plot = alt.Chart(table_new).mark_circle(size=60).encode(
            x=var1,
            y=var2,
            color = var3
        ).interactive()

        st.altair_chart(combined_plot, use_container_width=True)


    st.header("trial type 'column' only")
    # trial type 'column' only

    col1_fil, col2_fil = st.columns(2, gap="medium")

    with col1_fil:

        options_one_fil = table_new.columns
        var1_fil = st.selectbox("Select the Measurement variable you want to visualize on the X-axis",
                        options = options_one_fil)
        var1_series = table_new[var1]

    with col2_fil:

        options_two_fil = table_new.columns
        var2_fil = st.selectbox("Select the Stress variables you want to visualize on the Y-axis",
                        options=options_two_fil)
        var2_series = table_new[var2]

    table_trial_type_column = table_new[table_new["trial_type"] == 'column']

    combined_plot_filtered = alt.Chart(table_trial_type_column).mark_circle(size = 60).encode(
        x = var1_fil,
        y = var2_fil,
        tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
    ).interactive()

    st.altair_chart(combined_plot_filtered, use_container_width=True)

    #add_color_var = st.checkbox("Add color indicator variable: ")

