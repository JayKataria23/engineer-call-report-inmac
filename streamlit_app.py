import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection, execute_query
from datetime import datetime
import pytz


st.set_page_config(page_title='Support Ticket Workflow', page_icon='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAY1BMVEX////9+PjXjI6+P0K/QkXBSErpv8D14+PJZWi6MTS7NTjFVljryMjCT1G6MjW7Njm5LTDTfoDgqaq4Jir67+/ThIbx19fz3d3doqP25+fIYGPReXvdnqDYkpP79PTluLm+QELIVu6CAAAAy0lEQVR4AX2SBQ7DQAwEHc4xlMP//2TpnNJGHbFW2pGBPsjyokxUNf3StEI+EaqBUBvrnvhAQCxkCncRsv3BplDKI4SnVrgnQmV/lAfIsrPjVlFvKLnVmgsqOw59j8q6TEppIyoHkZS2OqKy9zxIu6FU3OrHCcLZcmtZozJfW7sTKtdBxGFPRN/DHAtWuohTRs9KowkIr0FQORnBp9wYRHOrLGcCzju+iDrilKvS9nsIG7UqB0LlwsqixnCQT5zo8CL7sJRlcUd8v9YNS1IRq/svf5IAAAAASUVORK5CYII=')
st.image("https://i0.wp.com/inmac.co.in/wp-content/uploads/2022/09/INMAC-web-logo.png?w=721&ssl=1")
st.title( 'Ticket Update')

conn = st.connection("supabase",type=SupabaseConnection)
engineers = list(pd.DataFrame(execute_query(conn.table("Engineers").select("name", count="None"), ttl=None).data)["name"])
engineerInput = st.selectbox("Engineer", options=engineers, index=None)
ids = pd.DataFrame(execute_query(conn.table("Logs").select("id", count="None").eq("completed", False), ttl=None).data)["id"].to_list()
idInput = st.selectbox("Ticket ID", options=ids, index=None)
current_datetime = datetime.now(pytz.timezone('Asia/Kolkata'))
current_time = current_datetime.time()
if idInput is not "" and idInput is not None:
    data = execute_query(conn.table("Logs").select("*", count="None").eq('id', idInput), ttl=None).data[0]
    completed = data["completed"]
    completedAt = data["completed_at"]
    callReport = data["call_report"]
    with st.form('Ticket', clear_on_submit=True):
        col1Completed, col2Completed = st.columns([1,1])
        with col1Completed:
            completedDate = st.date_input("Completed At", disabled=True)
        with col2Completed:
            completedTime = st.time_input("Completed At", value=current_time, disabled=True)
        newCallReportInput = st.file_uploader(label="Call Report", type=["png", "jpg", "jpeg", "webp", "pdf"], accept_multiple_files=False)
        save = st.form_submit_button("Save Report")
    
    if save:
        filename=""
        if not isinstance(newCallReportInput, str):
            filename = "call_reports/"+str(datetime.now())+newCallReportInput.__getattribute__("name")
            conn.upload("images", "local",newCallReportInput , filename)
        execute_query(conn.table('Logs').update([{
            "completed":str(True),
            "completed_at": str(datetime.combine(completedDate, completedTime)),
            "call_report":[filename],
        }]).eq("id", idInput), ttl='0')