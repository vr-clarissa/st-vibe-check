import streamlit as st
import pandas as pd
import gspread
import os
from google.oauth2.service_account import Credentials


def initialize_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Create API client
    if os.path.exists(".streamlit/secrets.toml"):
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.Client(auth=credentials)
    else:
        client = None

    return client


def load_google_sheet(client):
    if client is None:
        st.warning("WARNING: No credentials found. Loading local data.")
        google_sheet = None
    else:
        google_sheet = client.open("mood_log").get_worksheet(0)

    return google_sheet


def update_google_sheet(google_sheet, df):
    google_sheet.update([df.columns.values.tolist()] + df.values.tolist())

    return
