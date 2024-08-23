import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title='Support Ticket Workflow')
st.title( 'Update Engineer')

conn = st.connection("supabase",type=SupabaseConnection)


engineers = list(pd.DataFrame(execute_query(conn.table("Engineers").select("name", count="None"), ttl=None).data)["name"])

engineerInput = st.selectbox("Engineer", options=engineers, index=None)

if engineerInput:
    df = pd.DataFrame(execute_query(conn.table("Logs").select("*", count="None"), ttl="0").data)[["id", "created_at", "location", "priority", "problem", "engineer", "image", "completed", "completed_at", "call_report", "serialNumbers", "activeTime", "pause"]]
    ticketInput = st.selectbox("Ticked ID", options=list(df[(df["completed"]==False) & (df["engineer"]==engineerInput)]["id"]), index=None)
    if ticketInput:
        with st.form("Update Ticket"):
            updateDate = st.date_input("Date", disabled=True)
            updateTime = st.time_input("Time", disabled=True)
            callReport = st.file_uploader(label="Call Reports", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False)
            note = st.text_area("Note")
            b1, b2 = st.columns(2)
            complete = b1.form_submit_button("Complete Call", use_container_width=True)
            pending = b2.form_submit_button("Pending Call", use_container_width=True, type="primary")
        
        if complete:   
            if callReport is None:
                st.error("Please upload file first")
            else:
                st.write(callReport)
                filename = "call_reports/"+str(datetime.now())+callReport.__getattribute__("name")
                conn.upload("images", "local",callReport , filename)
                execute_query(conn.table('Logs').update([{
                                "completed":str(True),
                                "completed_at": str(datetime.combine(updateDate, updateTime)),
                                "call_report":[filename],
                        }]).eq("id",ticketInput), ttl='0')
                st.rerun()
        
        if pending:   
            if callReport is None:
                st.error("Please upload call report first")
            else:
                if note.strip() == "":
                    st.error("Please provide a note of why the call is pending")
                else:
                    msg = EmailMessage()
                    sender = "support@inmac.co.in"
                    password = "uoah pwps rblc mypr"
                    to = ["support@inmac.co.in", "repairs@inmac.co.in"]
                    content =  note
                    msg['From'] = sender
                    msg['Subject'] = "Call not complete "+engineerInput+" "+ticketInput
                    msg.set_content(content)
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                        smtp.login(sender, password)
                        msg['to'] = to
                        smtp.send_message(msg)
                        st.success("Email Sent!")
                
            
            
