import streamlit as st


def show_footer(in_sidebar=False):
    margin_top = "0.75rem" if in_sidebar else "2.5rem"
    st.html(
        f"""
        <div style="
            text-align: center;
            padding: 0.85rem 0.5rem;
            margin-top: {margin_top};
            border-top: 1px solid #334155;
        ">
            <p style="
                color: #94A3B8;
                font-size: 0.78rem;
                letter-spacing: 0.01em;
                margin: 0;
                font-weight: 500;
            ">
                Created by Astik Saini, Meet Goyal, Gaurav Singh, Shubham Kumar
            </p>
        </div>
        """
    )
