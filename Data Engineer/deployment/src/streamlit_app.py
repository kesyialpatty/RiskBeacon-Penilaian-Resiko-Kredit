import streamlit as st

try:
    from .data_pipeline import render_data_pipeline
    from .eda import render_eda
    from .home_page import render_home
    from .prediction import render_prediction
except ImportError:
    from data_pipeline import render_data_pipeline
    from eda import render_eda
    from home_page import render_home
    from prediction import render_prediction


def main():
    st.set_page_config(
        page_title="Credit Delinquency Demo",
        layout="wide",
    )

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Prediction", "EDA", "Pipeline"],
    )

    if page == "Home":
        render_home()
    elif page == "Prediction":
        render_prediction()
    elif page == "EDA":
        render_eda()
    else:
        render_data_pipeline()


if __name__ == "__main__":
    main()
