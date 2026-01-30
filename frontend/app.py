import os
from datetime import date, datetime, time

import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Personal Dashboard MVP", layout="wide")


def api_request(method, path, payload=None, params=None):
    url = f"{st.session_state.api_url}{path}"
    try:
        response = requests.request(
            method,
            url,
            json=payload,
            params=params,
            timeout=10,
        )
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None

    if not response.ok:
        st.error(f"API error {response.status_code}: {response.text}")
        return None

    if response.content:
        return response.json()
    return None


def build_datetime_payload(date_value, time_value):
    if date_value is None:
        return None
    time_value = time_value or time(0, 0)
    return datetime.combine(date_value, time_value)


def fetch_entries(category):
    data = api_request("GET", f"/{category}")
    return data or []


def render_table(title, entries):
    st.subheader(title)
    if not entries:
        st.info("No entries yet.")
        return None
    df = pd.DataFrame(entries)
    st.dataframe(df, use_container_width=True)
    return df


def render_update_form(category, fields, tz_default):
    entries = fetch_entries(category)
    entries_by_id = {entry["id"]: entry for entry in entries}

    with st.expander("Edit or delete entry"):
        entry_id = st.number_input(
            f"{category} entry id",
            min_value=1,
            step=1,
            format="%d",
            key=f"{category}_edit_id",
        )

        if st.button("Delete entry", key=f"{category}_delete_btn"):
            if entry_id in entries_by_id:
                api_request("DELETE", f"/{category}/{entry_id}")
                st.success("Entry deleted.")
            else:
                st.error("Entry id not found.")

        if entry_id not in entries_by_id:
            st.info("Enter a valid entry id to edit.")
            return

        current = entries_by_id[entry_id]
        with st.form(f"{category}_update_form"):
            date_value = None
            time_value = None
            if current.get("recorded_at"):
                dt_value = datetime.fromisoformat(current["recorded_at"])
                date_value = dt_value.date()
                time_value = dt_value.time()
            elif current.get("local_date"):
                date_value = date.fromisoformat(current["local_date"])

            updated_payload = {}
            recorded_at = build_datetime_payload(
                st.date_input(
                    "Date",
                    value=date_value or date.today(),
                    key=f"{category}_update_date",
                ),
                st.time_input(
                    "Time",
                    value=time_value or time(0, 0),
                    key=f"{category}_update_time",
                ),
            )
            updated_payload["recorded_at"] = recorded_at.isoformat() if recorded_at else None
            updated_payload["timezone"] = st.text_input(
                "Timezone",
                value=current.get("timezone") or tz_default,
                key=f"{category}_update_tz",
            )

            for field_name, field_config in fields.items():
                value = current.get(field_name)
                if field_config["type"] == "number":
                    if field_config.get("optional"):
                        raw = st.text_input(
                            field_config["label"],
                            value="" if value is None else str(value),
                            key=f"{category}_update_{field_name}",
                        )
                        updated_payload[field_name] = float(raw) if raw else None
                    else:
                        updated_payload[field_name] = st.number_input(
                            field_config["label"],
                            value=float(value) if value is not None else 0.0,
                            key=f"{category}_update_{field_name}",
                        )
                elif field_config["type"] == "int":
                    updated_payload[field_name] = st.number_input(
                        field_config["label"],
                        value=int(value) if value is not None else 0,
                        step=1,
                        key=f"{category}_update_{field_name}",
                    )
                else:
                    updated_payload[field_name] = st.text_input(
                        field_config["label"],
                        value=value or "",
                        key=f"{category}_update_{field_name}",
                    )

            submitted = st.form_submit_button("Update entry")
            if submitted:
                api_request("PUT", f"/{category}/{entry_id}", updated_payload)
                st.success("Entry updated.")


def render_time_series(entries, metrics, title):
    if not entries:
        st.info("No data for chart.")
        return
    df = pd.DataFrame(entries)
    if df.empty:
        st.info("No data for chart.")
        return
    df["local_date"] = pd.to_datetime(df["local_date"])
    df = df.sort_values("local_date").set_index("local_date")
    st.subheader(title)
    st.line_chart(df[metrics])


st.sidebar.header("Settings")
default_api_url = os.getenv("API_URL", "http://localhost:8000")
st.session_state.api_url = st.sidebar.text_input(
    "API base URL",
    value=st.session_state.get("api_url", default_api_url),
)
default_tz = st.sidebar.text_input("Default timezone", value="UTC")

tabs = st.tabs(
    [
        "Health",
        "Finance",
        "Productivity",
        "Learning",
        "Dashboard",
        "Export",
    ]
)

health_fields = {
    "sleep_hours": {"label": "Sleep hours", "type": "number"},
    "energy_level": {"label": "Energy level (1-10)", "type": "int"},
    "supplements": {"label": "Supplements", "type": "text"},
    "weight_kg": {"label": "Weight (kg)", "type": "number", "optional": True},
    "wellbeing": {"label": "Wellbeing (1-10)", "type": "int"},
    "notes": {"label": "Notes", "type": "text"},
}

finance_fields = {
    "income": {"label": "Income", "type": "number"},
    "expense_food": {"label": "Food expenses", "type": "number"},
    "expense_transport": {"label": "Transport expenses", "type": "number"},
    "expense_health": {"label": "Health expenses", "type": "number"},
    "expense_other": {"label": "Other expenses", "type": "number"},
    "notes": {"label": "Notes", "type": "text"},
}

productivity_fields = {
    "deep_work_hours": {"label": "Deep work hours", "type": "number"},
    "tasks_completed": {"label": "Tasks completed", "type": "int"},
    "focus_level": {"label": "Focus level (1-10)", "type": "int"},
    "notes": {"label": "Notes", "type": "text"},
}

learning_fields = {
    "study_hours": {"label": "Study hours", "type": "number"},
    "topics": {"label": "Topics", "type": "text"},
    "projects": {"label": "Projects", "type": "text"},
    "notes": {"label": "Notes", "type": "text"},
}


with tabs[0]:
    st.header("Health")
    with st.form("health_form"):
        date_value = st.date_input("Date", key="health_date")
        time_value = st.time_input("Time", key="health_time")
        sleep_hours = st.number_input("Sleep hours", min_value=0.0, max_value=24.0)
        energy_level = st.number_input("Energy level (1-10)", min_value=1, max_value=10, step=1)
        supplements = st.text_input("Supplements")
        weight_raw = st.text_input("Weight (kg)")
        wellbeing = st.number_input("Wellbeing (1-10)", min_value=1, max_value=10, step=1)
        notes = st.text_input("Notes")
        timezone = st.text_input("Timezone", value=default_tz, key="health_tz")
        submitted = st.form_submit_button("Add health entry")

        if submitted:
            recorded_at = build_datetime_payload(date_value, time_value)
            weight_kg = float(weight_raw) if weight_raw else None
            payload = {
                "recorded_at": recorded_at.isoformat() if recorded_at else None,
                "timezone": timezone,
                "sleep_hours": sleep_hours,
                "energy_level": energy_level,
                "supplements": supplements or None,
                "weight_kg": weight_kg,
                "wellbeing": wellbeing,
                "notes": notes or None,
            }
            api_request("POST", "/health", payload)
            st.success("Health entry saved.")

    health_entries = fetch_entries("health")
    render_table("Health entries", health_entries)
    render_update_form("health", health_fields, default_tz)


with tabs[1]:
    st.header("Finance")
    with st.form("finance_form"):
        date_value = st.date_input("Date", key="finance_date")
        time_value = st.time_input("Time", key="finance_time")
        income = st.number_input("Income", min_value=0.0)
        expense_food = st.number_input("Food expenses", min_value=0.0)
        expense_transport = st.number_input("Transport expenses", min_value=0.0)
        expense_health = st.number_input("Health expenses", min_value=0.0)
        expense_other = st.number_input("Other expenses", min_value=0.0)
        notes = st.text_input("Notes", key="finance_notes")
        timezone = st.text_input("Timezone", value=default_tz, key="finance_tz")
        submitted = st.form_submit_button("Add finance entry")

        if submitted:
            recorded_at = build_datetime_payload(date_value, time_value)
            payload = {
                "recorded_at": recorded_at.isoformat() if recorded_at else None,
                "timezone": timezone,
                "income": income,
                "expense_food": expense_food,
                "expense_transport": expense_transport,
                "expense_health": expense_health,
                "expense_other": expense_other,
                "notes": notes or None,
            }
            api_request("POST", "/finance", payload)
            st.success("Finance entry saved.")

    finance_entries = fetch_entries("finance")
    render_table("Finance entries", finance_entries)
    render_update_form("finance", finance_fields, default_tz)


with tabs[2]:
    st.header("Productivity")
    with st.form("productivity_form"):
        date_value = st.date_input("Date", key="productivity_date")
        time_value = st.time_input("Time", key="productivity_time")
        deep_work_hours = st.number_input("Deep work hours", min_value=0.0, max_value=24.0)
        tasks_completed = st.number_input("Tasks completed", min_value=0, step=1)
        focus_level = st.number_input("Focus level (1-10)", min_value=1, max_value=10, step=1)
        notes = st.text_input("Notes", key="productivity_notes")
        timezone = st.text_input("Timezone", value=default_tz, key="productivity_tz")
        submitted = st.form_submit_button("Add productivity entry")

        if submitted:
            recorded_at = build_datetime_payload(date_value, time_value)
            payload = {
                "recorded_at": recorded_at.isoformat() if recorded_at else None,
                "timezone": timezone,
                "deep_work_hours": deep_work_hours,
                "tasks_completed": tasks_completed,
                "focus_level": focus_level,
                "notes": notes or None,
            }
            api_request("POST", "/productivity", payload)
            st.success("Productivity entry saved.")

    productivity_entries = fetch_entries("productivity")
    render_table("Productivity entries", productivity_entries)
    render_update_form("productivity", productivity_fields, default_tz)


with tabs[3]:
    st.header("Learning")
    with st.form("learning_form"):
        date_value = st.date_input("Date", key="learning_date")
        time_value = st.time_input("Time", key="learning_time")
        study_hours = st.number_input("Study hours", min_value=0.0, max_value=24.0)
        topics = st.text_input("Topics")
        projects = st.text_input("Projects")
        notes = st.text_input("Notes", key="learning_notes")
        timezone = st.text_input("Timezone", value=default_tz, key="learning_tz")
        submitted = st.form_submit_button("Add learning entry")

        if submitted:
            recorded_at = build_datetime_payload(date_value, time_value)
            payload = {
                "recorded_at": recorded_at.isoformat() if recorded_at else None,
                "timezone": timezone,
                "study_hours": study_hours,
                "topics": topics or None,
                "projects": projects or None,
                "notes": notes or None,
            }
            api_request("POST", "/learning", payload)
            st.success("Learning entry saved.")

    learning_entries = fetch_entries("learning")
    render_table("Learning entries", learning_entries)
    render_update_form("learning", learning_fields, default_tz)


with tabs[4]:
    st.header("Dashboard")

    health_entries = fetch_entries("health")
    render_time_series(health_entries, ["sleep_hours", "energy_level", "wellbeing"], "Health trends")

    finance_entries = fetch_entries("finance")
    render_time_series(
        finance_entries,
        ["income", "expense_food", "expense_transport", "expense_health", "expense_other"],
        "Finance trends",
    )

    productivity_entries = fetch_entries("productivity")
    render_time_series(
        productivity_entries,
        ["deep_work_hours", "tasks_completed", "focus_level"],
        "Productivity trends",
    )

    learning_entries = fetch_entries("learning")
    render_time_series(learning_entries, ["study_hours"], "Learning trends")

    st.subheader("Correlations")
    correlations = api_request("GET", "/analytics/correlations")
    if correlations and correlations.get("correlations"):
        st.dataframe(pd.DataFrame(correlations["correlations"]), use_container_width=True)
    else:
        st.info("No correlations yet.")

    st.subheader("Insights")
    insights = api_request("GET", "/analytics/insights")
    if insights and insights.get("insights"):
        for item in insights["insights"]:
            st.write(f"- {item['message']}")
    else:
        st.info("No insights yet.")


with tabs[5]:
    st.header("Export CSV")
    category = st.selectbox(
        "Category",
        ["daily", "health", "finance", "productivity", "learning"],
    )
    if st.button("Download CSV"):
        response = requests.get(
            f"{st.session_state.api_url}/export",
            params={"category": category},
            timeout=10,
        )
        if response.ok:
            st.download_button(
                label="Save file",
                data=response.text,
                file_name=f"{category}.csv",
                mime="text/csv",
            )
        else:
            st.error(f"Export failed: {response.status_code}")
