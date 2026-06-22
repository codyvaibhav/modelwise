import streamlit as st
import pandas as pd
import plotly_express as px
from config import (
    main, base,
    get_data,
    get_base_data,
    get_overall_comparison_data,
    get_domestic_comparison_data,
    get_export_comparison_data,
    get_asrdata
)
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message="Workbook contains no default style*")

def show():
    st.set_page_config(page_title=f"{main} Summary", page_icon="📋", layout="wide")

    @st.cache_data
    def load_all_data():
        df = get_data()
        df_base = get_base_data()
        overall_data = get_overall_comparison_data()
        domestic_data = get_domestic_comparison_data()
        export_data = get_export_comparison_data()
        df5 = get_asrdata()
        return df, df_base, *overall_data, *domestic_data, *export_data, df5

    df, df_base, df2, imp_overall, sell_out_overall, df3, sell_out_domestic, launch_date, df4, sell_out_export, df5 = load_all_data()
    def generate_symptom_table(data, sell_out):
        # Count occurrences of each symptom
        symptom_counts = data['Symptom Group 1'].value_counts().reset_index()
        symptom_counts.columns = ['Symptom', 'Total']

        # Select top 6 symptoms
        top_symptoms = symptom_counts.head(6)

        # Calculate total count for top 6
        total_count = top_symptoms['Total'].sum()

        if total_count == 0:
            empty_top = pd.DataFrame({
                'Symptom': ['No defects found'] + [''] * 5,
                'Total': [''] * 6,
                'Contr.': [''] * 6,
                'PPM': ['-'] * 6
            })

            # Create total row
            total_row = pd.DataFrame({
                'Symptom': ['Total'],
                'Total': [0],
                'Contr.': ['0%'],
                'PPM': [0]
            })
            return pd.concat([empty_top, total_row], ignore_index=True), "No defects"

        # Calculate Contribution (%)
        top_symptoms['Contr.'] = (top_symptoms['Total'] / total_count * 100).round().astype(int)
        top_symptoms['Contr.'] = top_symptoms['Contr.'].astype(str) + '%'

        # Calculate PPM
        top_symptoms['PPM'] = (top_symptoms['Total'] / sell_out * 1000000).round().astype(int)

        # Create total row
        total_row = pd.DataFrame({
            'Symptom': ['Total'],
            'Total': [total_count],
            'Contr.': ['100%'],
            'PPM': [round(total_count / sell_out * 1000000)]
        })

        # Combine top symptoms and total row
        final_table = pd.concat([top_symptoms, total_row], ignore_index=True)

        top_2 = top_symptoms.head(2)['Symptom'].tolist()
        if len(top_2) == 0:
            remarks = "No defects"
        elif len(top_2) == 1:
            remarks = f"{top_2[0]} is the top defect."
        else:
            remarks = f"{top_2[0]} and {top_2[1]} are top defects"

        return final_table, remarks

    st.markdown(
        f"<h1 style='text-align: center;'>{main} Model Comparison : {imp_overall} from its Base Model</h1>",
        unsafe_allow_html=True
    )

    l,x, m,y, r = st.columns([4,1,4,1,4])
    with l:
        st.markdown('<p style="font-weight: bold; color: #131FAB; font-size: 2rem;">Overall</p>',unsafe_allow_html=True)
        st.write("")
        html_table = df2.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)

        st.write("")
        overall_table, remarks_overall = generate_symptom_table(df, sell_out_overall)
        html_table = overall_table.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align: left; font-size: 20px; color: #1E90FF;">*{remarks_overall} overall.</div>',
            unsafe_allow_html=True
        )
    with m:
        st.markdown('<p style="font-weight: bold; color: #131FAB; font-size: 2rem;">Domestic</p>',unsafe_allow_html=True)
        st.write("")
        html_table = df3.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)

        st.write("")
        domestic_df = df[df['RHQ'] == 'S.W.Asia']
        domestic_table, remarks_domestic = generate_symptom_table(domestic_df, sell_out_domestic)
        html_table = domestic_table.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align: left; font-size: 20px; color: #1E90FF;">*{remarks_domestic} in domestic market.</div>',
            unsafe_allow_html=True
        )
    with r:
        st.markdown('<p style="font-weight: bold; color: #131FAB; font-size: 2rem;">Export</p>',unsafe_allow_html=True)
        st.write("")
        html_table = df4.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)

        st.write("")
        export_df = df[df['RHQ'] != 'S.W.Asia']
        export_table, remarks_export = generate_symptom_table(export_df, sell_out_export)
        html_table = export_table.to_html(
            escape=False,
            index=False,
            classes="summary-table table3rd-col-bold"
        )
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align: left; font-size: 20px; color: #1E90FF;">*{remarks_export} in export market.</div>',
            unsafe_allow_html=True
        )

    st.write(" ")
    st.write(" ")

    total_days = len(get_asrdata())
    l, r, e = st.columns([5,5,1])
    with l:
        if total_days < 45:
            # Original View (Both Models)
                fig = px.line(
                    df5,
                    x="Day",
                    y=["main_ratio", "base_ratio"],
                    title="Day Wise Comparison",
                    labels={"value": "Ratio", "Day": "Day"},
                    color_discrete_sequence=["blue", "#FC580A"]
                )

                # Update traces to add markers
                fig.update_traces(
                    mode='lines+markers',
                    textposition='top center',
                )

                # Set trace names
                fig.data[0].name = f"{main}"
                fig.data[1].name = f"{base}"

                # Calculate indices for markers and annotations
                divPoints = max(1, len(df5) // 6)
                indices = list(range(0, len(df5), divPoints))
                if len(df5) - 1 not in indices:
                    indices.append(len(df5) - 1)

                marker_size = [6 if i in indices else 0 for i in range(len(df5))]

                fig.data[0].marker = dict(size=marker_size, color='blue', opacity=0.9)
                fig.data[1].marker = dict(size=marker_size, color='#FC580A', opacity=0.9)

                # Add annotations only for selected indices
                for i in indices:
                    row = df5.iloc[i]
                    fig.add_annotation(
                        x=row['Day'],
                        y=row['main_ratio'],
                        text=f"{row['main_ratio']:.2f}",
                        showarrow=False,
                        yshift=-10,
                        font=dict(size=10, color='blue')
                    )
                    # Annotation for S25U
                    fig.add_annotation(
                        x=row['Day'],
                        y=row['base_ratio'],
                        text=f"{row['base_ratio']:.2f}",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=10, color='#FC580A')
                    )

                fig.update_layout(
                    xaxis=dict(showgrid=False, showline=False,title=None),
                    yaxis=dict(showgrid=False,title=None),
                    legend_title_text="",
                    plot_bgcolor="#E8EDF2",
                    xaxis_tickfont_family="Arial",
                    xaxis_tickfont_size=12,
                    yaxis_tickfont_family="Arial",
                    yaxis_tickfont_size=12,
                )
                st.plotly_chart(fig)

        else:
                # Assuming df5 contains 'Week', 'main_ratio', and 'base_ratio' columns
                # Extract week number if not already done
                df5['week_num'] = df5['Week'].str.split().str[1].astype(int)

                # Calculate weekly averages for both models
                df_weekly = df5.groupby(['Week', 'week_num'], as_index=False).agg({
                    'main_ratio': 'mean',
                    'base_ratio': 'mean'
                }).sort_values('week_num')

                # Create comparison chart
                fig = px.line(
                    df_weekly,
                    x="Week",
                    y=["main_ratio", "base_ratio"],
                    title="Week Wise Defect Rate",
                    labels={"value": "Ratio", "variable": "Model"},
                    color_discrete_sequence=["blue", "#FC580A"]
                )

                # Update traces to add markers and set names
                fig.update_traces(
                    mode='lines+markers',
                    marker=dict(size=7, opacity=0.9),
                    hovertemplate = '%{fullData.name}: %{y:.2f}<extra></extra>',
                )

                # Set trace names
                fig.data[0].name = f"{main}"
                fig.data[1].name = f"{base}"

                for i, row in df_weekly.iterrows():
                    fig.add_annotation(
                        x=row['Week'],
                        y=row['main_ratio'],
                        text=f"{row['main_ratio']:.2f}",
                        showarrow=False,
                        yshift=-15,
                        font=dict(size=10, color='blue')
                    )
                    # Annotation for S25U (below the line)
                    fig.add_annotation(
                        x=row['Week'],
                        y=row['base_ratio'],
                        text=f"{row['base_ratio']:.2f}",
                        showarrow=False,
                        yshift=15,
                        font=dict(size=10, color='#FC580A')
                    )

                fig.update_layout(
                    hovermode='x unified',
                    xaxis=dict(
                        title=None,
                        showgrid=False,
                        showline=False,
                        tickmode='array',
                        showspikes=True,  # Enable vertical spike line
                        spikemode='across',  # Show spike across the whole plot
                        spikecolor='gray',
                        spikethickness=1,
                    ),
                    yaxis=dict(showgrid=False,title=None),
                    legend_title_text="",
                    plot_bgcolor="#E8EDF2",
                    xaxis_tickfont_family="Arial",
                    xaxis_tickfont_size=12,
                    yaxis_tickfont_family="Arial",
                    yaxis_tickfont_size=12,
                )
                st.plotly_chart(fig)

    with e:
        options = ['Top 5'] + df['Symptom Group 1'].value_counts().nlargest(5).index.tolist()
        symptom = st.selectbox("Symptom",options = options, index = 0)

    with r:
        if symptom == 'Top 5':
            top_symptoms = df['Symptom Group 1'].value_counts().nlargest(5).index.tolist()
            df_top = df[df['Symptom Group 1'].isin(top_symptoms)]
            df_weekly = df_top.groupby(['WK', 'Symptom Group 1', 'week_num']).size().reset_index(name='Count')
            df_weekly = df_weekly.sort_values('week_num')
            custom_colors = [
                '#540d6e', '#36369C', '#ffd23f', '#3bceac', '#0ead69',
            ]

            # Create line multiple chart
            fig = px.line(
                df_weekly,
                x='WK',
                y='Count',
                color='Symptom Group 1',
                title='Symptom Wise Trend',
                labels={'Count': '', 'WK': ''},
                text='Count',
                color_discrete_sequence=custom_colors
            )

            fig.update_traces(
                mode='lines+markers+text',  # Show text on markers
                textposition='top center',
                textfont=dict(size=10, color='black'),
                marker=dict(size=7, opacity=0.9),
                hovertemplate='%{y}<extra></extra>'
            )

            # Customize layout
            fig.update_layout(
                hovermode='x unified',  # Shows data for all traces at the hovered x-value
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    showline=False,
                    tickmode='array',
                    tickvals=df_weekly['WK'].unique(),
                    ticktext=df_weekly['WK'].unique(),
                    showspikes=True,  # Enable vertical spike line
                    spikemode='across',  # Show spike across the whole plot
                    spikecolor='gray',
                    spikethickness=1,
                ),
                yaxis=dict(showgrid=False,title=None),
                legend_title_text=None,
                plot_bgcolor='#E8EDF2',
                xaxis_tickfont_family='Arial',
                xaxis_tickfont_size=12,
                yaxis_tickfont_family='Arial',
                yaxis_tickfont_size=12,
            )

            # Ensure x-axis labels are in chronological order
            fig.update_xaxes(categoryorder='array',
                             categoryarray=sorted(df_weekly['WK'].unique(), key=lambda x: int(x.split()[1])))

            st.plotly_chart(fig)
        else:
            df_single = df[df['Symptom Group 1'] == symptom]
            df_weekly = df_single.groupby(['WK', 'week_num']).size().reset_index(name='Count')
            df_weekly = df_weekly.sort_values('week_num')

            # Create single line chart
            fig = px.line(
                df_weekly,
                x='WK',
                y='Count',
                title=f'{symptom} Trend',
                labels={'Count': '', 'WK': ''},
                text='Count',
                color_discrete_sequence=['#36369C']  # Use primary color
            )

            fig.update_traces(
                mode='lines+markers+text',
                textposition='top center',
                textfont=dict(size=10, color='black'),
                marker=dict(size=7, opacity=0.9),
                line=dict(width=3),  # Slightly thicker line for emphasis
                hovertemplate='%{y}<extra></extra>'
            )

            # Customize layout (consistent with Top 5 chart)
            fig.update_layout(
                hovermode='x unified',
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    showline=False,
                    tickmode='array',
                    tickvals=df_weekly['WK'].unique(),
                    ticktext=df_weekly['WK'].unique(),
                    showspikes=True,
                    spikemode='across',
                    spikecolor='gray',
                    spikethickness=1,
                ),
                yaxis=dict(showgrid=False,title=None),
                plot_bgcolor='#E8EDF2',
                xaxis_tickfont_family='Arial',
                xaxis_tickfont_size=12,
                yaxis_tickfont_family='Arial',
                yaxis_tickfont_size=12,
                showlegend=False  # No need for legend with single line
            )

            # Ensure chronological order
            fig.update_xaxes(
                categoryorder='array',
                categoryarray=sorted(df_weekly['WK'].unique(), key=lambda x: int(x.split()[1]))
            )

            st.plotly_chart(fig)
