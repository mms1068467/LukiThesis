import streamlit as st
from pathlib import Path
import os
import pandas as pd
import numpy as np
import scipy

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

    trial_type_options = list(table_new.trial_type.unique())
    trial_type_selection = st.multiselect("Pick the trial type(s) you want to analyze:",
                   trial_type_options,
                   trial_type_options)
    
    st.write("You selected the following trial type(s): ", trial_type_selection)

    table_filtered = table_new[table_new["trial_type"].isin(trial_type_selection)]
    st.write(f"Data before filtering {len(table_new)} \n Data after filtering trial type: {len(table_filtered)}")

    st.header("Self-chosen visuals:")

    simple_linechart = st.sidebar.checkbox("Simple Linechart")
    cumsum_linechart = st.sidebar.checkbox("Cumulative Sum Linechart")


    stacked_barchart_text = st.sidebar.checkbox("Stacked Bar Chart with text overlay")
    violin_chart = st.sidebar.checkbox("Violin Plot to compare distributions")

    scatter_href = st.sidebar.checkbox("Scatter Plots with href")

    #line_chart = st.sidebar.checkbox("Linechart")

    radial_chart = st.sidebar.checkbox("Radial Chart")
    pie_chart = st.sidebar.checkbox("Pie Chart")
    layered_hist = st.sidebar.checkbox("Layered Histogram")

    simple_hist = st.sidebar.checkbox("Simple Histogram")
    
    simple_scatter = st.sidebar.checkbox("Simple Scatter plot")

    multifeature_scatter = st.sidebar.checkbox("Multifeature Scatter plot")

    #### Simple line chart

    if simple_linechart:

        st.subheader("Line Chart over years")
        table_filtered_grouped_year = table_filtered[["year", "Reference"]].groupby("year").count().reset_index()
    #st.write(table_filtered_grouped_year)
        linechart_years = alt.Chart(table_filtered_grouped_year).mark_line().encode(
        x = "year:N", # TODO - 
        y = "Reference"
        ).interactive()
    
        st.altair_chart(linechart_years, use_container_width = True)

        # TODO - 

    #     st.subheader("Line Chart subs_cat")
    #     st.write(table_filtered.subs_cat.unique())
    #     table_filtered_grouped_year = table_filtered[["year", "subs_cat"]].groupby("subs_cat").sum().reset_index()
    #     st.write(table_filtered_grouped_year)
    # #st.write(table_filtered_grouped_year)
    #     linechart_years = alt.Chart(table_filtered_grouped_year).mark_line().encode(
    #     x = "year:N", # TODO - 
    #     y = "subs_cat"
    #     ).interactive()
    
    #     st.altair_chart(linechart_years, use_container_width = True)

        st.subheader("Variable selection for simple line chart:")

        col1_sel, col2_sel = st.columns(2, gap="medium")

        with col1_sel:

            options_var_one = table_filtered[["year"]].columns
            var1_selection = st.selectbox("Select variable you want to visualize on the X-axis",
                            options = options_var_one)
            var1_variable = table_filtered[var1_selection]

        with col2_sel:

            options_var_two = table_filtered.columns
            var2_selection = st.selectbox("Select the variable you want to visualize on the Y-axis",
                            options=options_var_two)
            
            var2_variable = table_filtered[var2_selection]


        st.subheader(f"Number of {var2_selection} per year")
        table_selected_grouped_year = table_filtered[[var1_selection, var2_selection]].groupby(var1_selection).count().reset_index()
    #st.write(table_filtered_grouped_year)
        linechart = alt.Chart(table_selected_grouped_year).mark_line().encode(
        x = "year:N", # TODO - 
        y = var2_selection,
        #tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
        # ).properties(
        # title = "Title"
        ).interactive()

        # linechart = alt.Chart(table_filtered).mark_line().encode(
        # x = var1_selection,
        # y = var2_selection,
        # tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
        # ).interactive()

        st.altair_chart(linechart, use_container_width=True)

    if radial_chart:
        st.subheader("Radial Chart for subs_cat")

        table_filtered_subs_cat = table_filtered[["subs_cat", "Unnamed: 0"]]
        
        table_filtered_subs_cat = table_filtered_subs_cat.groupby("subs_cat").count().reset_index()
        table_filtered_subs_cat = table_filtered_subs_cat.rename(columns = {"subs_cat": "subs_cat_type", "Unnamed: 0": "subs_cat_count"})


        base = alt.Chart(table_filtered_subs_cat).encode(
            alt.Theta("subs_cat_count:Q").stack(True),
            alt.Radius("subs_cat_count").scale(type="sqrt", zero=True, rangeMin=20),
            color="subs_cat_type:N",
        )

        c1 = base.mark_arc(innerRadius=20, stroke="#fff")

        c2 = base.mark_text(radiusOffset=10).encode(text="subs_cat_count:Q")

        st.altair_chart(c1 + c2)

    if pie_chart:
        table_filtered_gdl_subs = table_filtered[["gdl_subs", "Unnamed: 0"]]
        
        table_filtered_gdl_subs = table_filtered_gdl_subs.groupby("gdl_subs").count().reset_index()
        table_filtered_gdl_subs = table_filtered_gdl_subs.rename(columns = {"gdl_subs": "gdl_subs_type", "Unnamed: 0": "gdl_subs_count"})

        alt.Chart(table_filtered).mark_arc().encode(
            theta="gdl_subs_count",
            color="gdl_subs_type"
        )

    if cumsum_linechart:
        st.subheader("Cumulative Sum Line Chart Country")

        table_filtered_grouped_year_country = table_filtered[["year", "country"]].groupby("year").count().reset_index()

        cumsum_country = alt.Chart(table_filtered_grouped_year_country, width=600).mark_line().transform_window(
            # Sort the data chronologically
            sort=[{'field': 'year'}],
            # Include all previous records before the current record and none after
            # (This is the default value so you could skip it and it would still work.)
            frame=[None, 0],
            # What to add up as you go
            cumulative_country='sum(country)'
        ).encode(
            x='year:O',
            # Plot the calculated field created by the transformation
            y='cumulative_country:Q'
        )

        st.altair_chart(cumsum_country, use_container_width=True)

        st.subheader("Cumulative Sum Line Chart Subs_cat")
    
        table_filtered_grouped_year_subscat = table_filtered[["year", "subs_cat"]].groupby("year").count().reset_index()

        cumsum_subs_cat = alt.Chart(table_filtered_grouped_year_subscat, width=600).mark_line().transform_window(
            # Sort the data chronologically
            sort=[{'field': 'year'}],
            # Include all previous records before the current record and none after
            # (This is the default value so you could skip it and it would still work.)
            frame=[None, 0],
            # What to add up as you go
            cumulative_subs_cat='sum(subs_cat)'
        ).encode(
            x='year:O',
            # Plot the calculated field created by the transformation
            y='cumulative_subs_cat:Q'
        )
        
        st.altair_chart(cumsum_subs_cat, use_container_width=True)

        st.header("old code placeholder")

        table_filtered_grouped_year_trialtype = table_filtered[["year", "trial_type"]].groupby("year").count().reset_index()    
    

        cumsum = alt.Chart(table_filtered_grouped_year_trialtype).mark_line().encode(
        x = "year:O",
        y = "sum(trial_type)"
        ).interactive()
    
        st.altair_chart(cumsum, use_container_width = True)

        st.subheader("Variable selection for simple line chart:")

        col1_sel, col2_sel = st.columns(2, gap="medium")

        with col1_sel:

            options_var_one = table_filtered.columns
            var1_selection = st.selectbox("Select variable you want to visualize on the X-axis",
                            options = options_var_one)
            var1_variable = table_filtered[var1_selection]

        with col2_sel:

            options_var_two = table_filtered.columns
            var2_selection = st.selectbox("Select the variable you want to visualize on the Y-axis",
                            options=options_var_two)
            
            var2_variable = table_filtered[var2_selection]

        st.write("not implemented")

        #st.altair_chart(linechart, use_container_width=True)


    ### new selection
    if stacked_barchart_text:

        table_filtered_grouped_trial_type_subs_cat = table_filtered[["trial_type", "subs_cat"]].groupby(["trial_type"]).count().reset_index()        
        st.write(table_filtered_grouped_trial_type_subs_cat)

        st.subheader("Stacked bar chart")
    #     bars = alt.Chart(table_filtered_grouped_trial_type_subs_cat).mark_bar().encode(
    #     x=alt.X('subs_cat:N').stack('zero'),
    #     y=alt.Y('trial_type'),
    #     #color=alt.Color('site')
    # )

    #     text = alt.Chart(table_filtered_grouped_trial_type_subs_cat).mark_text(dx=-15, dy=3, color='white').encode(
    #         x=alt.X('subs_cat:N').stack('zero'),
    #         y=alt.Y('trial_type'),
    #         #detail='site:N',
    #         #text=alt.Text('sum(subs_cat)', format='.1f')
    #     )

        bars = alt.Chart(table_filtered_grouped_trial_type_subs_cat).mark_bar().encode(
        x=alt.X('trial_type'),
        y=alt.Y('subs_cat'),
        #y=alt.Y('subs_cat:N').stack('zero'),
        #color=alt.Color('site')
    )

        text = alt.Chart(table_filtered_grouped_trial_type_subs_cat).mark_text(dx=-15, dy=3, color='white').encode(
            x=alt.X('trial_type'),
            y=alt.Y('subs_cat'),
            #y=alt.Y('subs_cat:N').stack('zero'),
            #detail='site:N',
            #text=alt.Text('sum(subs_cat)', format='.1f')
        )

        st.altair_chart(bars + text, use_container_width = True)
        

    if violin_chart:
        st.subheader("Violin bar chart")

        table_filtered_pH_subs_cat = table_filtered[["pH", "subs_cat"]].dropna()

        pHmin = table_filtered_pH_subs_cat.pH.min()
        pHmax = table_filtered_pH_subs_cat.pH.max()

        violin_plot = alt.Chart(table_filtered_pH_subs_cat, width=100).transform_density(
            'pH',
            as_=['pH', 'density'],
            extent=[pHmin, pHmax],
            groupby=['subs_cat']
        ).mark_area(orient='horizontal').encode(
            alt.X('density:Q')
                .stack('center')
                .impute(None)
                .title(None)
                .axis(labels=False, values=[0], grid=False, ticks=True),
            alt.Y('pH:Q'),
            alt.Color('subs_cat:N'),
            alt.Column('subs_cat:N')
                .spacing(0)
                .header(titleOrient='bottom', labelOrient='bottom', labelPadding=0)
        ).configure_view(
            stroke=None
        )

        st.altair_chart(violin_plot)

    if scatter_href:
        st.subheader("Scatter Plots with href")

        scatter_plot_load_vs_ox = alt.Chart(table_filtered).mark_circle(size = 60).encode(
            alt.X("ox_eff_avg").axis(format='%'),
            alt.Y("load_avg"),  
            tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
        ).interactive()

        scatter_reg = scatter_plot_load_vs_ox + scatter_plot_load_vs_ox.transform_regression("load_avg", "ox_eff_avg").mark_line() 
        st.altair_chart(scatter_reg, use_container_width=True)
        

        col1, col2 = st.columns(2, gap="medium")

        with col1:

            options_one = table_filtered[["ox_eff_avg"]].columns
            var1 = st.selectbox("Please select the Measurement variable you want to visualize on the X-axis",
                            options = options_one)
            var1_series = table_filtered[var1]

        with col2:

            options_two = table_filtered[["pH", "compaction", "bulk_dens", "poros", "wc", "whc", "RA7",
              "el_cond", "amb_temp", "in_temp", "oc", "mc", "ch4_conc"]].columns
            

            #options_two = table_filtered.columns
            var2 = st.selectbox("Please select the Stress variables you want to visualize on the Y-axis",
                            options=options_two)
            var2_series = table_filtered[var2]
        
        #table_filtered = table_filtered.dropna()


        scatter_plot = alt.Chart(table_filtered).mark_circle(size = 60).encode(
            alt.X("ox_eff_avg").axis(format='%'),
            y = var2,
            tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
        ).interactive()

        st.altair_chart(scatter_plot, use_container_width=True)
        
        add_regression_line = st.checkbox("Add regression line")
        if add_regression_line:

            scatter_with_regline = scatter_plot + scatter_plot.transform_regression(var1, var2).mark_line(color="red")
            st.altair_chart(scatter_with_regline, use_container_width=True)
        

        add_color_var = st.checkbox("Add 'subs_cat' or other variable as color")
        if add_color_var:
            options_three = table_filtered[["subs_cat"]].columns

            var3 = st.selectbox("Select variable for coloring:",
                                options=options_three
                                )
            
            var3_series = table_filtered[var3]

            combined_plot_data = pd.concat([var1_series, var2_series, var3_series], axis=1)

            combined_plot = alt.Chart(combined_plot_data).mark_circle(size=60).encode(
                x=alt.X(f"{var1}").axis(format='%'),
                y=var2,
                color = var3
            ).interactive()

            st.altair_chart(combined_plot, use_container_width=True)
        
        add_color_var_trial = st.checkbox("Add 'trial_type' or other variable as color")
        if add_color_var_trial:
            options_three = table_filtered[["trial_type"]].columns

            var3 = st.selectbox("Select variable for coloring:",
                                options=options_three
                                )
            
            var3_series = table_filtered[var3]

            combined_plot_data = pd.concat([var1_series, var2_series, var3_series], axis=1)

            combined_plot = alt.Chart(combined_plot_data).mark_circle(size=60).encode(
                x=alt.X(f"{var1}").axis(format='%'),
                y=var2,
                color = var3
            ).interactive()

            #st.altair_chart(combined_plot + combined_plot.transform_regression(var1_series, var2_series).mark_line())

            st.altair_chart(combined_plot, use_container_width=True)

    if simple_scatter:
        st.subheader("Simple Scatter Plots")

        table_filtered = table_filtered[["load_avg", "ox_eff_avg"]]
        simple_scatter_plot = alt.Chart(table_filtered).mark_circle(size = 60).encode(
            x = "load_avg",
            y = alt.Y("ox_eff_avg").axis(format='%'),
        ).interactive()

        st.altair_chart(simple_scatter_plot, use_container_width=True)

        add_regression_line = st.checkbox("Add regression line:")
        if add_regression_line:
        
            corr_table = table_filtered[["load_avg", "ox_eff_avg"]].dropna()

            st.write(f'Correlation (Person): {scipy.stats.pearsonr(corr_table["load_avg"], corr_table["ox_eff_avg"])[0]}')
            st.write(f'Correlation (Spearman): {scipy.stats.spearmanr(corr_table["load_avg"], corr_table["ox_eff_avg"])[0]}')
            st.write(f'Correlation (Kendall): {scipy.stats.kendalltau(corr_table["load_avg"], corr_table["ox_eff_avg"])[0]}')


            simple_scatter_plot_with_line = simple_scatter_plot + simple_scatter_plot.transform_regression("load_avg", "ox_eff_avg").mark_line(color = "red") 
            st.altair_chart(simple_scatter_plot_with_line, use_container_width=True)
        

    if multifeature_scatter:
        st.subheader("Multifeature Scatter Plots")

        col1_m, col2_m = st.columns(2, gap="medium")

        with col1_m:

            options_one = table_filtered[["pH", "compaction", "bulk_dens", "poros", "wc", "whc", "RA7",
              "el_cond", "amb_temp", "in_temp", "oc", "mc", "ch4_conc"]].columns
            

            #options_two = table_filtered.columns
            var1_m = st.selectbox("Please select the Stress variables you want to visualize on the X-axis",
                            options=options_one)
            var1_series_m = table_filtered[var1_m]

        with col2_m:
            options_two = table_filtered[["load_avg"]].columns
            var2_m = st.selectbox("Please select the Measurement variable you want to visualize on the Y-axis",
                            options = options_two)
            var2_series_m = table_filtered[var2_m]



        combined_plot = alt.Chart(table_filtered).mark_circle(size = 60).encode(
            x = var1_m,
            y = var2_m,
            tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
        ).interactive()

        st.altair_chart(combined_plot, use_container_width=True)



        add_regression_line = st.checkbox("Add regression line:")
        if add_regression_line:

            st.write("Variable 1 is: ", var1_m)
            st.write("Variable 2 is: ", var2_m)

        
            corr_table = table_filtered[[var1_m, var2_m]].dropna()

            st.write(f"Correlation (Person): {scipy.stats.pearsonr(corr_table[var1_m], corr_table[var2_m])[0]}")
            st.write(f"Correlation (Spearman): {scipy.stats.spearmanr(corr_table[var1_m], corr_table[var2_m])[0]}")
            st.write(f"Correlation (Kendall): {scipy.stats.kendalltau(corr_table[var1_m], corr_table[var2_m])[0]}")


            final_plot = combined_plot + combined_plot.transform_regression(var1_m, var2_m).mark_line(color = "red") 
            st.altair_chart(final_plot, use_container_width=True)

        add_color_var = st.checkbox("Add 'ox_eff_avg' or other variable as color")
        if add_color_var:
            options_three = table_filtered[["ox_eff_avg"]].columns

            var3_m = st.selectbox("Select variable for coloring:",
                                options=options_three
                                )
            
            var3_series_m = table_filtered[var3_m]

            combined_plot_data = pd.concat([var1_series_m, var2_series_m, var3_series_m], axis=1)

            combined_plot = alt.Chart(combined_plot_data).mark_circle(size=60).encode(
                x=var1_m,
                y=var2_m,
                color = var3_m
            ).interactive()

            st.altair_chart(combined_plot, use_container_width=True)

    if simple_hist:
        hist_cols = ["gdl_cm",
                "col_rad",
                "load_avg",
                "ox_avg",
                "ox_eff_avg",
                "days",
                "subs_cm"]

        options = table_filtered[hist_cols].columns
        

        #options_two = table_filtered.columns
        var_selected = st.selectbox("Please select the variables to visualize in Histogram",
                        options=options)
        var_var_selected = table_filtered[var_selected]

        st.subheader("Histogram subs_cm")
        simple_hist = alt.Chart(table_filtered).mark_bar().encode(
            alt.X(f"{var_selected}:Q", bin=True),
            y='count()',
        )

        st.altair_chart(simple_hist, use_container_width=True)


    if layered_hist:


        rel_cols = ["gdl_cm", "col_rad", "load_avg given", "load_avg derived", "load_avg estimated",
                   "ox_avg given", "ox_avg derived", "ox_avg estimated",
                   "ox_eff_avg given", "ox_eff_avg derived", "ox_eff_avg estimated",
                   "days given", "days derived", "days estimated"]
        
        histogram_variable_selection = st.multiselect("Pick the column(s) you want to visualize in layered histogram:",
                   table_filtered.columns,
                   default = ["gdl_cm", "pH", "col_rad"],
                   placeholder="Select up to 3 desired columns ...")

        
        table_filtered_hist_vars = table_filtered[histogram_variable_selection]
        
        if len(histogram_variable_selection) == 1:
            simple_hist = alt.Chart(table_filtered_hist_vars).mark_bar().encode(
                alt.X(f"{histogram_variable_selection[0]}:Q", bin=True),
                y='count()',
            )

            st.altair_chart(simple_hist, use_container_width=True)


        if len(histogram_variable_selection) == 2:

            layered_hist_plot = alt.Chart(table_filtered_hist_vars).transform_fold(
                [histogram_variable_selection[0], histogram_variable_selection[1]],
                as_=['Experiment', 'Measurement']
            ).mark_bar(
                opacity=0.3,
                binSpacing=0
            ).encode(
                alt.X('Measurement:Q').bin(maxbins=100),
                alt.Y('count()').stack(None),
                alt.Color('Experiment:N')
            )

            st.altair_chart(layered_hist_plot, use_container_width=True)

        if len(histogram_variable_selection) == 3:

            layered_hist_plot = alt.Chart(table_filtered_hist_vars).transform_fold(
                [histogram_variable_selection[0], histogram_variable_selection[1], histogram_variable_selection[2]],
                as_=['Experiment', 'Measurement']
            ).mark_bar(
                opacity=0.3,
                binSpacing=0
            ).encode(
                alt.X('Measurement:Q').bin(maxbins=100),
                alt.Y('count()').stack(None),
                alt.Color('Experiment:N')
            )

            st.altair_chart(layered_hist_plot, use_container_width=True)
    
    strip_plot = st.sidebar.checkbox("Strip Plot with Jitter")
    if strip_plot:
        strip_fig = alt.Chart(table_filtered).mark_tick().encode(
            x='gdl_cm:Q',
            y='trial_type:O'
        )

        st.altair_chart(strip_fig, use_container_width=True)

    correlation_plot = st.sidebar.checkbox("Show correlations")
    if correlation_plot:
        st.write("Correlations")
        table_filtered_corr = table_filtered[["pH", "compaction", "bulk_dens", "poros", "wc", "whc", "RA7", "el_cond", "amb_temp", "in_temp",
        "oc", "col_rad", "days", "subs_cm", "gdl_cm", "year", "load_avg",
        "ox_eff_avg"]]
        corr = table_filtered_corr.corr()
        st.write(corr.style.background_gradient(cmap='coolwarm'))

    ##### CMD + Shift + /
    # col1, col2 = st.columns(2, gap="medium")

    # with col1:

    #     options_one = table_new.columns
    #     var1 = st.selectbox("Please select the Measurement variable you want to visualize on the X-axis",
    #                     options = options_one)
    #     var1_series = table_new[var1]

    # with col2:

    #     options_two = table_new.columns
    #     var2 = st.selectbox("Please select the Stress variables you want to visualize on the Y-axis",
    #                     options=options_two)
    #     var2_series = table_new[var2]


    # combined_plot = alt.Chart(table_new).mark_circle(size = 60).encode(
    #     x = var1,
    #     y = var2,
    #     tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
    # ).interactive()

    # st.altair_chart(combined_plot, use_container_width=True)

    # add_color_var = st.checkbox("Add color indicator variable: ")

    # if add_color_var:
    #     options_three = table_new.columns

    #     var3 = st.selectbox("Select variable for coloring:",
    #                         options=options_three)
    #     var3_series = table_new[var3]

    #     combined_plot_data = pd.concat([var1_series, var2_series, var3_series], axis=1)

    #     combined_plot = alt.Chart(table_new).mark_circle(size=60).encode(
    #         x=var1,
    #         y=var2,
    #         color = var3
    #     ).interactive()

    #     st.altair_chart(combined_plot, use_container_width=True)


    # st.header("trial type 'column' only")
    # # trial type 'column' only

    # col1_fil, col2_fil = st.columns(2, gap="medium")

    # with col1_fil:

    #     options_one_fil = table_new.columns
    #     var1_fil = st.selectbox("Select the Measurement variable you want to visualize on the X-axis",
    #                     options = options_one_fil)
    #     var1_series = table_new[var1]

    # with col2_fil:

    #     options_two_fil = table_new.columns
    #     var2_fil = st.selectbox("Select the Stress variables you want to visualize on the Y-axis",
    #                     options=options_two_fil)
    #     var2_series = table_new[var2]

    # table_trial_type_column = table_new[table_new["trial_type"] == 'column']

    # combined_plot_filtered = alt.Chart(table_trial_type_column).mark_circle(size = 60).encode(
    #     x = var1_fil,
    #     y = var2_fil,
    #     tooltip=["country", "year", "trial", "trial_type", "subs", "load_avg", "ox_eff_avg"]
    # ).interactive()

    # st.altair_chart(combined_plot_filtered, use_container_width=True)

    # #add_color_var = st.checkbox("Add color indicator variable: ")



    # # Number of countries conducting studies over the years
    # number_countries_per_year = table_new[["year", "country"]].groupby('year').count()
    # number_countries_per_year = number_countries_per_year.reset_index()
    # number_countries_per_year['year'] = number_countries_per_year['year'].astype(int) 
    # st.write(number_countries_per_year)

    # country_year_visual = alt.Chart(number_countries_per_year).mark_bar().encode(
    #     x = 'year',
    #     y = 'country'
    # ).properties(
    #     title = "Number of studies conducted per year"
    # ).interactive()

    # st.altair_chart(country_year_visual, use_container_width=True)

    # # Number of studies per Country 
    # number_studies_per_country = table_new[["year", "country"]].groupby('country').count()
    # number_studies_per_country = number_studies_per_country.reset_index()
    # number_studies_per_country['year'] = number_studies_per_country['year'].astype(int) 
    # st.write(number_studies_per_country)

    # country_studies_visual = alt.Chart(number_studies_per_country).mark_bar().encode(
    #     x = 'country',
    #     y = 'year'
    # ).properties(
    #     title = "Number of studies per country"
    # ).interactive()

    # st.altair_chart(country_studies_visual, use_container_width=True)

    # # TODO - check how these two categorical variables should be plotted

    # # Trial type (nur column) und subs_cat

    # trial_type_subs_cat = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    # x='subs_cat',
    # y='trial_type',
    # #size='gdl_subs',
    # color='subs_cat1'
    # ).properties(
    #     title = "Categorization of substrate (organic, mineral, …) per trial type"
    # ).interactive()

    # st.altair_chart(trial_type_subs_cat, use_container_width=True)

    # ########################## need to ask about this



    # # Trial type (nur column) und ox_eff_avg
    # trial_type_ox_eff_avg = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    # x='ox_eff_avg',
    # y='trial_type',
    # #size='gdl_subs',
    # color='subs_cat1'
    # ).properties(
    #     title = "Percentage of 'ox_avg' from 'load_avg' per trial type"
    # ).interactive()

    # st.altair_chart(trial_type_ox_eff_avg, use_container_width=True)



    # # Trial type (nur column) und load_avg und ox_avg (3 variablen möglich?)

    # load_ox_per_trial = alt.Chart(table_new).mark_circle(size = 60).encode(
    #     x = "load_avg",
    #     y = "ox_avg",
    #     color = "trial_type",
    #     tooltip = ["country", "year", "subs_cat", "pH", "ox_avg_type"]
    # ).properties(
    #     title = "Average influx of ch4 to subtrate vs. oxidised ch4 (trial type color-coded)"
    # ).interactive()
    # load_ox_per_trial.configure_header(
    #     titleColor='black',
    #     titleFontSize=14,
    # )

    # st.altair_chart(load_ox_per_trial, use_container_width=True)

    # # Trial type (nur column) und subs_cm
        
    # trial_type_subs_cm = alt.Chart(table_new, width=200, height=200).mark_circle().encode(
    # x='subs_cm',
    # y='trial_type',
    # #size='gdl_subs',
    # color='subs_cat1'
    # ).properties(
    #     title = "Height of methane oxidation layer per trial type"
    # ).interactive()

    # st.altair_chart(trial_type_subs_cm, use_container_width=True)

