import streamlit as st
import pandas as pd
import warnings
import datetime
import plotly.graph_objects as go

from gd_utils import initialize_client, load_google_sheet, update_google_sheet


def log_mood(google_client, mood, additionalNotes):
    google_sheet = load_google_sheet(client=google_client)
    df = pd.DataFrame(google_sheet.get_all_records())
    new_entry = pd.DataFrame([
        {
            "logTime": datetime.datetime.now().isoformat(),
            "mood": mood,
            "additionalNotes": additionalNotes
        }
    ])
    df = pd.concat([df, new_entry], ignore_index=True)
    update_google_sheet(google_sheet=google_sheet, df=df)
    return


def plot_bar_chart_by_today(google_client):
    google_sheet = load_google_sheet(client=google_client)
    df = pd.DataFrame(google_sheet.get_all_records())
    df["logTime"] = pd.to_datetime(df["logTime"])
    logs_today = df.loc[df["logTime"] < datetime.datetime.now().isoformat()].copy()
    mood_count = logs_today.groupby("mood", as_index=False).size()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=mood_count["mood"].values.tolist(),
            y=mood_count["size"].values.tolist()
        )
    )
    return fig


def plot_bar_chart_by_time_of_day(google_client):
    google_sheet = load_google_sheet(client=google_client)
    df = pd.DataFrame(google_sheet.get_all_records())
    df["logTime"] = pd.to_datetime(df["logTime"])
    df["timeOfDay"] = "Morning"
    df.loc[(df["logTime"].dt.hour >= 12) & (df["logTime"].dt.hour < 18), "timeOfDay"] = "Afternoon"
    df.loc[(df["logTime"].dt.hour >= 18) & (df["logTime"].dt.hour < 23), "timeOfDay"] = "Evening"
    df.loc[(df["logTime"].dt.hour >= 23) | (df["logTime"].dt.hour < 5), "timeOfDay"] = "Late Night"
    morning_mood_count = df[df["timeOfDay"]=="Morning"].groupby("mood", as_index=False).size()
    afternoon_mood_count = df[df["timeOfDay"]=="Afternoon"].groupby("mood", as_index=False).size()
    evening_mood_count = df[df["timeOfDay"]=="Evening"].groupby("mood", as_index=False).size()
    late_mood_count = df[df["timeOfDay"]=="Late Night"].groupby("mood", as_index=False).size()
    fig = go.Figure(data=[
        go.Bar(
            name="Morning Tickets",
            x=morning_mood_count["mood"].values.tolist(),
            y=morning_mood_count["size"].values.tolist(),
            marker_color="#FFA15A"
        ),
        go.Bar(
            name="Afternoon Tickets",
            x=afternoon_mood_count["mood"].values.tolist(),
            y=afternoon_mood_count["size"].values.tolist(),
            marker_color="#B6E880"
        ),
        go.Bar(
            name="Evening Tickets",
            x=evening_mood_count["mood"].values.tolist(),
            y=evening_mood_count["size"].values.tolist(),
            marker_color="#636EFA"
        ),
        go.Bar(
            name="Late Night Tickets",
            x=late_mood_count["mood"].values.tolist(),
            y=late_mood_count["size"].values.tolist(),
            marker_color="#7F7F7F"
        )
    ])
    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def get_notes(google_client):
    google_sheet = load_google_sheet(client=google_client)
    df = pd.DataFrame(google_sheet.get_all_records())
    notes_df = df.loc[df["additionalNotes"]!=""].copy()
    notes_df["logTime"] = pd.to_datetime(notes_df["logTime"]).dt.date

    custom_order = ["🤩", "🙂", "😕", "😔", "😡"]
    notes_df["mood"] = pd.Categorical(notes_df["mood"], categories=custom_order, ordered=True)
    notes_df.sort_values(by=["logTime", "mood"], ascending=[False, False], inplace=True)
    notes_df.reset_index(inplace=True, drop=True)
    notes_df.rename(
        columns={"logTime": "Log Entry Date", "mood": "Logged Mood", "additionalNotes": "Notes"},
        inplace=True
    )
    return notes_df


if __name__ == "__main__":
    # Page setup
    warnings.filterwarnings("ignore")
    st.set_page_config(
        page_title="Support Tickets Vibe Check",
    )

    app_container = st.container()
    with app_container:
        st.title("Support Tickets Vibe Check")

        if "google_client" not in st.session_state:
            st.session_state.google_client = initialize_client()

        form_tab, charts_tab, notes_tab = st.tabs(["🗃 Form Submission", "📈 Chart", "✏️ Notes"])

        with form_tab:
            st.caption(
                """
                Help us track the mood of the queue using the form below as directed:
                1. Select the emoji that most appropriately summarizes the overall vibe of the support ticket
                2. Optional: Add a short note to contextualize the emoji if necessary
                3. Click the 'Log Mood' button on to add to the tracker
                """
            )
            with st.form("vibe_check"):
                selected_emoji = st.selectbox(
                    label="Overall Mood",
                    options=["🤩", "🙂", "😕", "😔", "😡"],
                )
                input_notes = st.text_area(
                    label="Additional Context"
                )

                submitted = st.form_submit_button(label="Log Mood")
                if submitted:
                    log_mood(
                        google_client=st.session_state.google_client,
                        mood=selected_emoji,
                        additionalNotes=input_notes
                    )
                    st.success("Mood logged!")

        with charts_tab:
            st.markdown(
                """
                #### _Mood of the Queue_
                """
            )
            st.caption(
                f"""
                {datetime.datetime.today().strftime('%B %d, %Y')}
                """
            )
            day_bar_chart = plot_bar_chart_by_today(google_client=st.session_state.google_client)
            st.plotly_chart(day_bar_chart)

            st.markdown(
                """
                ### _Mood Trends Throughout the Day_
                """
            )
            st.caption(
                """
                A historic outlook on moods logged
                """
            )
            timed_bar_chart = plot_bar_chart_by_time_of_day(google_client=st.session_state.google_client)
            st.plotly_chart(timed_bar_chart)

        with notes_tab:
            st.caption(
                """
                Notes are automatically sorted by most recent entries, then by the mood.
                """
            )
            notes_df = get_notes(google_client=st.session_state.google_client)
            st.dataframe(notes_df, hide_index=True)
