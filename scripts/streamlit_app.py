import os
import streamlit as st
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import json
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Healthcare Analytics Dashboard started successfully!")

client = bigquery.Client()

dataset_id = 'healthcare_analytics'
patients_data_table = 'patients_data'
appointments_data_table = 'appointments_data'
cms_data_table = 'cms_data'

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

def load_lottie(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"Lottie animation file not found at {filepath}. Please ensure the file exists.")
        return None

def run_query(query):
    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()

def login_page():
    st.title("Healthcare Analytics Dashboard - Login")
    st.markdown("---")
    
    lottie_animation = load_lottie(r"E:\healthcare_analytics\data\animation.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="login")
    
    st.subheader("User Login")
    if st.button("Login as User"):
        st.session_state.authenticated = True
        st.session_state.user_type = "user"
        st.rerun()
    
    st.markdown("---")
    st.subheader("Admin Login")
    password = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if password == "admin123":
            st.session_state.authenticated = True
            st.session_state.user_type = "admin"
            st.rerun()
        else:
            st.error("Incorrect admin password")

def admin_panel():
    st.title("Admin Panel")
    st.markdown("---")
    
    st.subheader("Execute Custom Query")
    query = st.text_area("Enter your SQL query:", height=200)
    
    if st.button("Execute Query"):
        if query.strip():
            with st.spinner("Executing query..."):
                result = run_query(query)
                if not result.empty:
                    st.success("Query executed successfully!")
                    st.dataframe(result)
                    
                    csv = result.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name='query_results.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("Query executed but returned no results.")
        else:
            st.warning("Please enter a query to execute.")
    
    st.markdown("---")
    st.subheader("Table Information")
    
    @st.cache_data(ttl=300)
    def get_all_tables():
        try:
            query = f"""
                SELECT table_name 
                FROM `{dataset_id}.INFORMATION_SCHEMA.TABLES`
                WHERE table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            tables_df = run_query(query)
            return {name.replace('_', ' ').title(): f"{dataset_id}.{name}" 
                   for name in tables_df['table_name']}
        except Exception as e:
            st.error(f"Failed to fetch tables: {str(e)}")
            return {
                "Patients Data": f"{dataset_id}.{patients_data_table}",
                "Appointments Data": f"{dataset_id}.{appointments_data_table}",
                "CMS Data": f"{dataset_id}.{cms_data_table}"
            }
    
    tables = get_all_tables()

    if st.button("Refresh Table List"):
        st.cache_data.clear()
        st.rerun()
    
    selected_table = st.selectbox("Select a table to view schema:", list(tables.keys()))
    
    if st.button("Show Schema"):
        schema_query = f"""
            SELECT column_name, data_type, is_nullable
            FROM `{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{tables[selected_table].split('.')[-1]}'
        """
        schema = run_query(schema_query)
        if not schema.empty:
            st.dataframe(schema)
        else:
            st.warning(f"Could not retrieve schema for {tables[selected_table]}")
    
    if st.button("Preview Data"):
        preview_query = f"SELECT * FROM `{tables[selected_table]}` LIMIT 10"
        preview_data = run_query(preview_query)
        if not preview_data.empty:
            st.dataframe(preview_data)
        else:
            st.warning(f"Could not retrieve data/The table '{selected_table}' exists but contains no data from {tables[selected_table]}")

def user_dashboard():
    st.title("Healthcare Provider Analytics Dashboard")
    st.markdown("---")

    lottie_animation = load_lottie(r"E:\healthcare_analytics\data\animation.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="dashboard")

    st.sidebar.title("Explore Insights")
    analysis_option = st.sidebar.selectbox(
        "Choose Analysis",
        ["Doctor Appointment Volume", 
         "Patient Appointment Patterns",
         "Facility Readmission Rates"]
    )

    if analysis_option == "Doctor Appointment Volume":
        st.header("Doctor Appointment Volume")
        
        query = f"""
            SELECT NAME AS `Doctor Name`, COUNT(*) AS `Appointments Count`
            FROM `{dataset_id}.{appointments_data_table}`
            GROUP BY `Doctor Name`
            ORDER BY `Appointments Count` DESC
        """
        df = run_query(query)

        df.index = df.index + 1

        search_query = st.text_input("Search by Doctor Name", "")
        if search_query:
            df = df[df['Doctor Name'].astype(str).str.contains(search_query, case=False)]

        page_size = 10
        page_number = st.number_input("Page Number", min_value=1, max_value=(len(df) // page_size) + 1, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size

        st.write("Appointments per Doctor")
        st.dataframe(df.iloc[start_idx:end_idx])

        visualization_option = st.radio(
            "Select Visualization Type",
            ["Page-Level Insights", "Full Data View"]
        )

        if visualization_option == "Page-Level Insights":
            data_to_visualize = df.iloc[start_idx:end_idx]
        else:
            data_to_visualize = df.head(10)

        st.write("Bar Chart: Doctors by Appointment Count")
        plt.figure(figsize=(10, 6))
        plt.bar(data_to_visualize['Doctor Name'], data_to_visualize['Appointments Count'], color='skyblue')
        plt.xlabel('Doctor Name')
        plt.ylabel('Appointments Count')
        plt.title(f'Doctors by Appointment Count ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

        st.write("Line Plot: Appointment Trends")
        plt.figure(figsize=(10, 6))
        plt.plot(data_to_visualize['Doctor Name'], data_to_visualize['Appointments Count'], marker='o', color='green')
        plt.xlabel('Doctor Name')
        plt.ylabel('Appointments Count')
        plt.title(f'Appointment Trends ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

        st.write("Scatter Plot: Appointment Distribution")
        plt.figure(figsize=(10, 6))
        plt.scatter(data_to_visualize['Doctor Name'], data_to_visualize['Appointments Count'], color='orange')
        plt.xlabel('Doctor Name')
        plt.ylabel('Appointments Count')
        plt.title(f'Appointment Distribution ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

    elif analysis_option == "Patient Appointment Patterns":
        st.header("Patient Appointment Patterns")
        
        query = f"""
            WITH appointment_dates AS (
                SELECT 
                    p.patient_name AS `Patient Name`,
                    PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', a.START) AS start_time,
                    PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', a.STOP) AS stop_time,
                    LAG(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', a.STOP)) OVER (PARTITION BY a.patient_id ORDER BY PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', a.START)) AS prev_stop_time
                FROM `{dataset_id}.{appointments_data_table}` a
                JOIN `{dataset_id}.{patients_data_table}` p ON a.patient_id = p.patient_id
            ),
            appointment_gaps AS (
                SELECT 
                    `Patient Name`,
                    DATE_DIFF(start_time, prev_stop_time, DAY) AS days_between_appointments
                FROM appointment_dates
                WHERE prev_stop_time IS NOT NULL
            )
            SELECT 
                `Patient Name`,
                AVG(days_between_appointments) AS `Average Days Between Appointments`
            FROM appointment_gaps
            GROUP BY `Patient Name`
            ORDER BY `Average Days Between Appointments` DESC
        """
        df = run_query(query)

        df.index = df.index + 1

        search_query = st.text_input("Search by Patient Name", "")
        if search_query:
            df = df[df['Patient Name'].astype(str).str.contains(search_query, case=False)]

        page_size = 10
        page_number = st.number_input("Page Number", min_value=1, max_value=(len(df) // page_size) + 1, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size

        st.write("Average Days Between Appointments")
        st.dataframe(df.iloc[start_idx:end_idx])

        visualization_option = st.radio(
            "Select Visualization Type",
            ["Page-Level Insights", "Full Data View"]
        )

        if visualization_option == "Page-Level Insights":
            data_to_visualize = df.iloc[start_idx:end_idx]
        else:
            data_to_visualize = df.head(10)

        st.write("Histogram: Distribution of Average Days Between Appointments")
        plt.figure(figsize=(10, 6))
        plt.hist(data_to_visualize['Average Days Between Appointments'], bins=20, color='lightgreen', edgecolor='black')
        plt.xlabel('Average Days Between Appointments')
        plt.ylabel('Frequency')
        plt.title(f'Distribution of Average Days Between Appointments ({visualization_option})')
        st.pyplot(plt)

        st.write("Scatter Plot: Average Days Between Appointments")
        plt.figure(figsize=(10, 6))
        plt.scatter(data_to_visualize['Patient Name'], data_to_visualize['Average Days Between Appointments'], color='purple')
        plt.xlabel('Patient Name')
        plt.ylabel('Average Days Between Appointments')
        plt.title(f'Scatter Plot: Average Days Between Appointments ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

        st.write("Line Plot: Appointment Trends Over Time")
        plt.figure(figsize=(10, 6))
        plt.plot(data_to_visualize['Patient Name'], data_to_visualize['Average Days Between Appointments'], marker='o', color='blue')
        plt.xlabel('Patient Name')
        plt.ylabel('Average Days Between Appointments')
        plt.title(f'Appointment Trends Over Time ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

    elif analysis_option == "Facility Readmission Rates":
        st.header("Facility Readmission Rates")
        
        query = f"""
            SELECT `Facility Name`, SUM(`Number of Readmissions`) AS `Total Readmissions`
            FROM `{dataset_id}.{cms_data_table}`
            GROUP BY `Facility Name`
            ORDER BY `Total Readmissions` DESC
        """
        df = run_query(query)

        df.index = df.index + 1

        search_query = st.text_input("Search by Facility Name", "")
        if search_query:
            df = df[df['Facility Name'].astype(str).str.contains(search_query, case=False)]

        page_size = 10
        page_number = st.number_input("Page Number", min_value=1, max_value=(len(df) // page_size) + 1, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size

        st.write("Readmissions by Facility")
        st.dataframe(df.iloc[start_idx:end_idx])

        visualization_option = st.radio(
            "Select Visualization Type",
            ["Page-Level Insights", "Full Data View"]
        )

        if visualization_option == "Page-Level Insights":
            data_to_visualize = df.iloc[start_idx:end_idx]
        else:
            data_to_visualize = df.head(10)

        st.write("Bar Chart: Facilities by Total Readmissions")
        plt.figure(figsize=(10, 6))
        plt.bar(data_to_visualize['Facility Name'], data_to_visualize['Total Readmissions'], color='salmon')
        plt.xlabel('Facility Name')
        plt.ylabel('Total Readmissions')
        plt.title(f'Facilities by Total Readmissions ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

        st.write("Pie Chart: Readmission Distribution by Facility")
        plt.figure(figsize=(8, 8))
        plt.pie(data_to_visualize['Total Readmissions'], labels=data_to_visualize['Facility Name'], autopct='%1.1f%%', startangle=140)
        plt.title(f'Readmission Distribution by Facility ({visualization_option})')
        st.pyplot(plt)

        st.write("Line Plot: Readmissions Trend")
        plt.figure(figsize=(10, 6))
        plt.plot(data_to_visualize['Facility Name'], data_to_visualize['Total Readmissions'], marker='o', color='red')
        plt.xlabel('Facility Name')
        plt.ylabel('Total Readmissions')
        plt.title(f'Readmissions Trend ({visualization_option})')
        plt.xticks(rotation=90)
        st.pyplot(plt)

if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.user_type == "admin":
        admin_panel()
    else:
        user_dashboard()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_type = None
        st.rerun()