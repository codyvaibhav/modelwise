import streamlit as st
from pages2 import summary, analysis, improvement
from config import main, marketing_name, last_updated
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message="Workbook contains no default style*")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(f"""
<div class="fdm-header">

  <!-- LEFT: FDM Logo -->
  <div class="fdm-logo">
    <span class="fdm-logo-mark">FDM</span>
    <span class="fdm-logo-sub">Field Defect Monitoring</span>
  </div>

  <!-- CENTER: Dashboard Title -->
  <div class="fdm-title-block">
    <h1>Field Defect Monitoring</h1>
  </div>

  <!-- RIGHT: Model & timestamp -->
  <div class="fdm-meta">
    <div class="model-tag">Model:<span>{marketing_name}</span></div>
    <div class="update-tag">⟳ Last updated: {last_updated}</div>
  </div>

</div>
""", unsafe_allow_html=True)

header_container = st.container()

with header_container:
    try:
        from streamlit_option_menu import option_menu

        NAV_PAGES = ["Summary", "Analysis", "Improvement"]
        NAV_ICONS = ["clipboard2-data","bar-chart-line", "graph-up-arrow"]

        selected = option_menu(
            menu_title=None,
            options=NAV_PAGES,
            icons=NAV_ICONS,
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "6px 2rem",
                    "background-color": "#F5F7FA",  # Light gray-blue
                    "border-radius": "20px",
                    "width": "100%",
                    "display": "flex",
                    "justify-content": "center",
                    "box-shadow": "0 2px 10px rgba(0,0,0,0.05)"  # Subtle depth
                },
                "icon": {
                    "color": "#5E7CE2",  # Soft periwinkle
                    "font-size": "2rem",
                },
                "nav-link": {
                    "font-family": "'Nunito', sans-serif",
                    "font-size": "1.5rem",
                    "font-weight": "600",
                    "color": "#5A6270",  # Medium gray-blue
                    "padding": "8px 22px",
                    "border-radius": "8px",
                    "border": "1px solid transparent",
                    "transition": "all 0.25s ease",
                },
                "nav-link:hover": {
                    "color": "#5E7CE2",  # Periwinkle accent
                    "background-color": "#052105",
                    "transform": "translateY(-1px)"
                },
                "nav-link-selected": {
                    "background-color": "rgba(123, 201, 167, 0.15)",  # Mint green
                    "color": "#4A9D75",  # Soft green
                    "font-weight": "700",
                    "border": "1px solid rgba(123, 201, 167, 0.25)",
                }
            }

        )

    except ImportError:
        # Graceful fallback if streamlit_option_menu is not installed
        selected = st.radio(
            "Navigation",
            options=["Summary", "Analysis", "Improvement"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
        )

# Page routing
if selected == "Summary":
    summary.show()
elif selected == "Analysis":
    analysis.show()
elif selected == "Improvement":
    improvement.show()