import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection, execute_query
from datetime import datetime


st.set_page_config(page_title='Support Ticket Workflow', page_icon='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAY1BMVEX////9+PjXjI6+P0K/QkXBSErpv8D14+PJZWi6MTS7NTjFVljryMjCT1G6MjW7Njm5LTDTfoDgqaq4Jir67+/ThIbx19fz3d3doqP25+fIYGPReXvdnqDYkpP79PTluLm+QELIVu6CAAAAy0lEQVR4AX2SBQ7DQAwEHc4xlMP//2TpnNJGHbFW2pGBPsjyokxUNf3StEI+EaqBUBvrnvhAQCxkCncRsv3BplDKI4SnVrgnQmV/lAfIsrPjVlFvKLnVmgsqOw59j8q6TEppIyoHkZS2OqKy9zxIu6FU3OrHCcLZcmtZozJfW7sTKtdBxGFPRN/DHAtWuohTRs9KowkIr0FQORnBp9wYRHOrLGcCzju+iDrilKvS9nsIG7UqB0LlwsqixnCQT5zo8CL7sJRlcUd8v9YNS1IRq/svf5IAAAAASUVORK5CYII=')
st.image("https://i0.wp.com/inmac.co.in/wp-content/uploads/2022/09/INMAC-web-logo.png?w=721&ssl=1")
st.title( 'Ticket Update')

conn = st.connection("supabase",type=SupabaseConnection)
ids = pd.DataFrame(execute_query(conn.table("Logs").select("id", count="None"), ttl=None).data)["id"].to_list()
idInput = st.selectbox("Ticket ID", options=ids, index=None)
if idInput is not "" and idInput is not None:
    data = execute_query(conn.table("Logs").select("*", count="None").eq('id', idInput), ttl=None).data[0]
    completed = data["completed"]
    completedAt = data["completed_at"]
    callReport = data["call_report"]
    problem = data["problem"]
    serialNumbers = data["serialNumbers"]
    with st.form('Ticket', clear_on_submit=True):
        problemInput = st.text_area("Problem Statement", value=problem)
        serialNumbers = st.text_area('Serial Number\'s', placeholder="Seperate with comma", value=",".join(serialNumbers))
        placeholderCompletedAt = st.empty()
        col1Completed, col2Completed = st.columns([1,1])
        with col1Completed:
                placeholderCompletedAt1 = st.empty() 
        with col2Completed:
                placeholderCompletedAt2 = st.empty() 

        placeholderCallReport1 = st.empty()
        placeholderCallReport2 = st.empty()
        placeholderCallReport3 = st.empty()

        save = st.form_submit_button("Save Report")
    
    with placeholderCompletedAt:
            completedInput = st.toggle("Completed", completed)

    if completedInput == True:
            if completed==False:
                    with placeholderCompletedAt1:    
                            completedDate = st.date_input("Completed At", value = None)
                    with placeholderCompletedAt2:
                            completedTime = st.time_input("Completed At", value = None)
            else:
                    with placeholderCompletedAt1:    
                            completedDate = st.date_input("Completed At", value = datetime.strptime(completedAt[0:10], "%Y-%m-%d"))
                    with placeholderCompletedAt2:
                            completedTime = st.time_input("Completed At", value = datetime.strptime(completedAt[12:20], "%H:%M:%S"))
    with placeholderCallReport1:
        newCallReportInput = st.file_uploader(label="Call Reports", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
    with placeholderCallReport2:
        callReportInput = st.multiselect("Call Reports", callReport+newCallReportInput, callReport+newCallReportInput)
    with placeholderCallReport3:
        if callReportInput != None:
            with st.container():
                for i in callReportInput:
                    if isinstance(i, str):
                        data = conn.download("images" ,source_path=i, ttl=None)
                        st.image(data[0])
                    else:
                        st.image(i)
    if save:
        serialNumbers = serialNumbers.replace(" ", "").split(",")
        for i in callReportInput:
            if not isinstance(i, str):
                filename = "call_reports/"+str(datetime.now())+i.__getattribute__("name")
                conn.upload("images", "local",i , filename)
                callReportInput.append(filename)
                callReportInput.remove(i)
        if completedInput:
            completed_at = str(datetime.combine(completedDate, completedTime))
        else:
            completed_at=None
        execute_query(conn.table('Logs').update([{
                                "problem":problemInput,
                                "serialNumbers":serialNumbers,
                                "completed":str(completedInput),
                                "completed_at": completed_at,
                                "call_report":callReportInput,
                        }]).eq("id",idInput), ttl='0')
        st.rerun()

