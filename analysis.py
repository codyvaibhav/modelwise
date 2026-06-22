import streamlit as st
import pandas as pd
import plotly_express as px
from datetime import datetime

from config import (
    main, base,
    get_data,
    get_base_data,
    get_asrdata,
    get_msclist
)
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message="Workbook contains no default style*")

def show():
    st.set_page_config(page_title=f"{main} Analysis", page_icon=":bar_chart:")
    st.title("Analysis with Filters")

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if 'script_start_time' not in st.session_state:
        st.session_state.script_start_time = datetime.now()

    @st.cache_data
    def load_all_data():
        return (
            get_data(),
            get_base_data(),
            get_asrdata(),
            get_msclist()
        )

    df, df_base, df2, df3 = load_all_data()

    df = pd.merge(df3, df, on="ASC Code", how="right")
    df["ASC name,code"] = df["ASC Name"].astype(str) + ", " + df["ASC Code"].astype(str)

    colors = [
        "#6565A1", "#326b77", "#568b87", "#80ae9a", "#b5d1ae", "#122740", "#DAF9DE", "#F6FFDC", "#F5F5F5", "#FAFAFA",
        "#6565A1", "#326b77", "#568b87", "#80ae9a", "#b5d1ae", "#122740", "#DAF9DE", "#F6FFDC", "#F5F5F5",
        "#6565A1", "#326b77", "#568b87", "#80ae9a", "#b5d1ae", "#122740", "#DAF9DE", "#F6FFDC", "#F5F5F5"
    ]
    # Initialize session state for day range if not exists
    if 'day_range_filter' not in st.session_state:
        min_day = int(df2['Day'].min())
        max_day = int(df2['Day'].max())
        st.session_state.day_range_filter = (min_day, max_day)

    # Create columns for symptom selection and day range
    l, r, apply, reset = st.columns([1, 1.66,0.17,0.17])
    with l:
        options = ['Top 5'] + df['Symptom Group 1'].unique().tolist()
        symptom = st.selectbox("Symptom", options=options, index=0)

    with r:
        min_day = int(df2['Day'].min())
        max_day = int(df2['Day'].max())

        # Create slider with session state
        day_range = st.slider(
            "Days",
            min_value=min_day,
            max_value=max_day,
            value=st.session_state.day_range_filter
        )

    with apply:
        apply_clicked = st.button("Apply")
    with reset:
        reset_clicked = st.button("Reset")

    # Handle Apply and Reset actions
    if apply_clicked:
        st.session_state.day_range_filter = day_range
        st.success("Filter applied!")
        st.rerun()

    if reset_clicked:
        st.session_state.day_range_filter = (min_day, max_day)
        st.success("Filter reset!")
        st.rerun()

    # Apply filter using session state values
    df = df[
        (df['Day'] >= st.session_state.day_range_filter[0]) &
        (df['Day'] <= st.session_state.day_range_filter[1])
        ]

    l, m, r = st.columns(3)
    with l:
        dfSelection = df
        if symptom == 'Top 5':
            symptomWiseCalls = dfSelection.groupby(by=["Symptom Group 1"]).size().reset_index(name="Count").sort_values(
                by="Count", ascending=False)
            n = 5
            top_n = symptomWiseCalls.head(n)
            total_count = symptomWiseCalls["Count"].sum()
            top_n["Percentage"] = (top_n["Count"] / total_count) * 100
            top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%")

            fig = px.bar(
                top_n,
                x="Symptom Group 1",
                y="Count",
                orientation="v",
                title="<b>Top 5 Symptoms</b>" if symptom == 'Top 5' else f"<b>Top Symptoms</b>",
                # color=dynamic_colors,
                template="plotly_white",
                text=top_n["PercentageLabel"],  # Display x% on bars
            )

            fig.update_traces(
                marker_color=colors[:len(top_n)],
                # marker_line_color='black',  # Optional: Add border color
                # marker_line_width=1.5,
                textfont=dict(size=14)  # Customize text font
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor="#E8EDF2",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                autosize=True,
                xaxis_tickfont_family="Arial",
                xaxis_tickfont_size=12,
                yaxis_tickfont_family="Arial",
                yaxis_tickfont_size=12,
                # xaxis_tickfont_color="black",
                # yaxis_tickfont_color="black",
            )
            st.plotly_chart(fig)
        else:
            total_defects = len(df)  # Use the unfiltered DataFrame

            # Filter for selected symptom
            dfSelection = df[df["Symptom Group 1"] == symptom]
            count_symptom = len(dfSelection)

            # Calculate percentage contribution
            contr = (count_symptom / total_defects) * 100 if total_defects > 0 else 0

            # Create percentage bar visualization
            fig = go.Figure()

            # Background bar (100% transparent)
            fig.add_trace(go.Bar(
                x=[100],
                y=[""],
                orientation='h',
                marker=dict(color='lightgray'),
                showlegend=False,
                hoverinfo='none'
            ))

            # Foreground bar (actual percentage)
            fig.add_trace(go.Bar(
                x=[contr],
                y=[""],
                orientation='h',
                marker=dict(color='#36369C'),
                text=[f"{contr:.2f}%"],
                textposition='outside',
                insidetextanchor='middle',
                showlegend=False,
                hoverinfo='none'
            ))

            # Update layout for clean appearance
            fig.update_layout(
                height=150,
                xaxis=dict(showticklabels=False, range=[0, 100], showgrid=False, zeroline=False),
                yaxis=dict(showticklabels=False, showgrid=False),
                barmode='overlay',
                margin=dict(l=20, r=20, t=0, b=20),
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig, width='content')
            # Display contribution message
            st.markdown(
                f'<div style="text-align: left; font-size: 20px; color: #1E90FF;">*{symptom} is contributing {contr:.2f}% of total defects.</div>',
                unsafe_allow_html=True
            )

    with r:
        subSymptomWise = dfSelection.groupby(by=["Symptom Group 2"]).size().reset_index(name="Count").sort_values(
            by="Count", ascending=False)
        n = min(5, len(subSymptomWise))
        top_n = subSymptomWise.head(n)

        total_count = subSymptomWise["Count"].sum()
        top_n["Percentage"] = (top_n["Count"] / total_count) * 100
        top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%")

        fig = px.bar(
            top_n,
            x="Count",
            y="Symptom Group 2",
            orientation="h",
            title="<b>Top 5 Sub-Symptoms</b>" if symptom == 'Top 5' else f"<b>Top Sub-Symptoms</b>",
            template="plotly_white",
            text=top_n["PercentageLabel"],
        )

        fig.update_traces(
            marker_color=colors[:len(top_n)],
            textfont=dict(size=16)
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="#E8EDF2",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, autorange="reversed"),
            autosize=True,
            xaxis_tickfont_family="Arial",
            xaxis_tickfont_size=12,
            yaxis_tickfont_family="Arial",
            yaxis_tickfont_size=12,
        )
        st.plotly_chart(fig)
        with m:
            repairWiseCalls = dfSelection.groupby(by=["Repair Description"]).size().reset_index(
                name="Count").sort_values(
                by="Count", ascending=False)

            n = 5
            top_n = repairWiseCalls.head(n)
            total_count = repairWiseCalls["Count"].sum()
            top_n["Percentage"] = (top_n["Count"] / total_count) * 100
            top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%")

            fig = px.bar(
                top_n,
                x="Count",
                y="Repair Description",
                orientation="h",
                title="<b>Top 5 Repair Parts</b>" if symptom == 'Top 5' else f"<b>Top Repair Parts</b>",
                template="plotly_white",
                text=top_n["PercentageLabel"],
            )

            fig.update_traces(
                marker_color=colors[:len(top_n)],
                textfont=dict(size=16)
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor="#E8EDF2",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, autorange="reversed"),
                autosize=True,
                xaxis_tickfont_family="Arial",
                xaxis_tickfont_size=12,
                yaxis_tickfont_family="Arial",
                yaxis_tickfont_size=12,
            )
            st.plotly_chart(fig)

    l, m, r = st.columns(3)
    with l:
        stateWiseCalls = dfSelection.groupby(by=["Region(Coverage)"]).size().reset_index(name="Count").sort_values(
            by="Count",
            ascending=False)
        n = 5
        top_n = stateWiseCalls.head(n)

        total_count = stateWiseCalls["Count"].sum()
        top_n["Percentage"] = (top_n["Count"] / total_count) * 100
        top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%")

        fig = px.bar(
            top_n,
            x="Region(Coverage)",
            y="Count",
            orientation="v",
            title="<b>Top 5 States</b>" if symptom == 'Top 5' else f"<b>Top States</b>",
            template="plotly_white",
            text=top_n["PercentageLabel"],
        )

        fig.update_traces(
            marker_color=colors[:len(top_n)],
            textfont=dict(size=16)
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="#E8EDF2",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            autosize=True,
            xaxis_tickfont_family="Arial",
            xaxis_tickfont_size=12,
            yaxis_tickfont_family="Arial",
            yaxis_tickfont_size=12,
        )
        st.plotly_chart(fig)
    with m:
        locationWise = dfSelection.groupby(by=["Location"]).size().reset_index(name="Count").sort_values(
            by="Count", ascending=False)
        n = 5
        top_n = locationWise.head(n)
        total_count = locationWise["Count"].sum()
        top_n["Percentage"] = (top_n["Count"] / total_count) * 100

        top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%")

        fig = px.bar(
            top_n,
            x="Count",
            y="Location",
            orientation="h",
            title="<b>Top 5 Locations</b>" if symptom == 'Top 5' else f"<b>Top Locations</b>",
            template="plotly_white",
            text=top_n["PercentageLabel"],  # Display x% on bars
        )

        fig.update_traces(
            marker_color=colors[:len(top_n)],
            textfont=dict(size=16)
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="#E8EDF2",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, autorange="reversed"),
            autosize=True,
            xaxis_tickfont_family="Arial",
            xaxis_tickfont_size=12,
            yaxis_tickfont_family="Arial",
            yaxis_tickfont_size=12,
            # yaxis_tickfont_color="black",
        )
        st.plotly_chart(fig)

    with r:
        # dfSelection = dfSelection[dfSelection["ASC Name"].notnull()]

        branchWise = dfSelection.groupby(by=["ASC name,code"]).size().reset_index(name="Count").sort_values(by="Count",
                                                                                                            ascending=False)
        branchWise_nonzero = branchWise[branchWise["ASC name,code"] != 0]
        n = 5
        top_n = branchWise_nonzero.head(n)

        # total_count = branchWise["Count"].sum()
        # top_n["Percentage"] = (top_n["Count"] / total_count) * 100
        # top_n["PercentageLabel"] = top_n["Percentage"].apply(lambda x: f"{int(x)}%"

        # top_n["ASC Code Str"] = top_n["ASC Code"].astype(str)

        fig = px.bar(
            top_n,
            y="ASC name,code",
            x="Count",
            orientation="h",
            title="<b>Worst MSCs</b>",
            template="plotly_white",
            text="Count",
            labels={"ASC name,code": "ASC name, code", "Count": "Count"}
        )

        fig.update_traces(
            marker_color=colors[:len(top_n)],
            textfont=dict(size=16)
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="#E8EDF2",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, autorange="reversed"),
            autosize=True,
            xaxis_tickfont_family="Arial",
            xaxis_tickfont_size=12,
            yaxis_tickfont_family="Arial",
            yaxis_tickfont_size=12,
            # yaxis_tickfont_color="black",
        )
        st.plotly_chart(fig)

    # -------------------------------------

    st.markdown(
        "<h5 style='text-align: left; font-weight: bold;'>Check MSC Details</h3>",
        unsafe_allow_html=True
    )

    selected_asc = st.selectbox("Enter ASC Code", options=df["ASC Code"].unique())

    df_filtered = df[df["ASC Name"].notnull()]
    df_unique = df_filtered.drop_duplicates(subset=["ASC Code"])

    if selected_asc:
        result = df_unique[df_unique["ASC Code"] == selected_asc]

        if not result.empty:
            result_display = result[["ASC Code", "ASC Name", 'Region(Coverage)', "Location", "Region"]]
            html_table = result_display.to_html(
                index=False,
                classes="summary-table",
                escape=False
            )
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.warning(f"No details found for ASC Code: {selected_asc}")
    else:
        st.info("Please select an ASC Code")
