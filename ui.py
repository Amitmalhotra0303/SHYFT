import streamlit as st
import requests
import time

st.title("Multi-Agent Research Assistant")

API_URL = "http://localhost:8000"

topic = st.text_input("Enter research topic:", 
                     "The business and technical implications of AI agents in enterprise settings")

if st.button("Start Research"):
    response = requests.post(
        f"{API_URL}/research",
        json={"topic": topic, "depth": "balanced"}
    )
    
    if response.status_code == 200:
        task = response.json()
        st.session_state.task_id = task['id']
        st.success(f"Research task created with ID: {task['id']}")
    else:
        st.error("Failed to create research task")

if 'task_id' in st.session_state:
    st.subheader("Research Progress")
    progress_bar = st.progress(0)
    status_text = st.empty()
    activity_log = st.empty()
    
    while True:
        response = requests.get(
            f"{API_URL}/research/{st.session_state.task_id}/status"
        )
        
        if response.status_code == 200:
            task = response.json()
            progress_bar.progress(task['progress'])
            status_text.text(f"Status: {task['status']}")
            
            if task['status'] == 'completed':
                st.success("Research completed!")
                report_response = requests.get(
                    f"{API_URL}/research/{st.session_state.task_id}/report"
                )
                report = report_response.json()
                
                st.subheader("Research Report")
                st.markdown(report['report']['text'])
                
                st.subheader("Sources")
                for source in report['sources'][:10]:  # Show top 10 sources
                    st.caption(f"{source['title']} ({source['url']}) - Credibility: {source['credibility_score']:.2f}")
                break
                
            elif task['status'] == 'failed':
                st.error("Research failed")
                break
                
        time.sleep(2)