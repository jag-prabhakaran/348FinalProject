import streamlit as st
import pandas as pd
from db import *  
import plotly.express as px

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Login":
            st.title("Login")
            username = st.text_input("Username")
            if username == "riya":
                st.balloons()
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if authenticate_user(username, password):
                    if username == "riya":
                        st.balloons()
                    st.session_state['logged_in'] = True
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect username or password")

        
        elif choice == "Register":
            st.title("Register")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Create Account"):
                if create_user(username, password):
                    st.success("User created successfully! Please go to the Login page.")
                else:
                    st.error("Username already exists")
    
    else:
        task_manager_app()

def task_manager_app():
    st.markdown("""
        <div style="background-color:#2E4053; padding:10px; border-radius:10px; margin-bottom:20px;">
            <h1 style="color:white; text-align:center; font-family: 'Arial', sans-serif; font-weight: bold; letter-spacing: 1px;">Dynamic Task Prioritizer</h1>
        </div>
    """, unsafe_allow_html=True)

    menu = ["Home", "Create Task", "View Tasks", "Update Task", "Delete Task"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("## Welcome to the Dynamic Task Prioritizer!")
        st.write("Navigate using the menu on the left to manage your tasks effectively.")

        tasks_data = view_all_data("Default")  
        if tasks_data:
            df = pd.DataFrame(tasks_data, columns=["Title", "Priority", "Status", "Date", "Description"])

            status_counts = df['Status'].value_counts()
            fig = px.pie(names=status_counts.index, values=status_counts.values, title="Tasks Status Overview")
            st.plotly_chart(fig, use_container_width=True)

            st.write("## High Priority Tasks")
            high_priority_tasks = df[df['Priority'] == 'High']
            if not high_priority_tasks.empty:
                st.dataframe(high_priority_tasks[['Title', 'Status', 'Date', 'Description']])
            else:
                st.write("")


    elif choice == "Create Task":
        with st.form(key='create_task'):
            st.write("## Add New Task")
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Task Description")
            task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            task_status = st.selectbox("Status", ["ToDo", "Doing", "Done"])
            task_due_date = st.date_input("Due Date")
            submit_button = st.form_submit_button(label='Add Task')

            if submit_button:
                add_data(task_title, task_priority, task_status, task_due_date, task_description)
                st.success(f"Added Task: '{task_title}' with priority '{task_priority}', status '{task_status}' due by {task_due_date}")

    if choice == "View Tasks":
        st.write("## View Tasks")
        
        view_option = st.selectbox("View Options", ["All Tasks", "Filter by Priority", "Summary by Status"], index=0)
        
        if view_option == "All Tasks":
            sort_option = st.selectbox("Sort By", ["Default", "Priority", "Due Date"], index=0)
            result = view_all_data(sort_option)
            
            if result:
                clean_df = pd.DataFrame(result, columns=["Title", "Priority", "Status", "Date", "Description"])
                st.dataframe(clean_df)
            else:
                st.info("No tasks found.")
        
        elif view_option == "Filter by Priority":
            priority = st.selectbox("Select Priority", ["High", "Medium", "Low"])
            filtered_tasks = filter_tasks_by_priority(priority)
            if filtered_tasks:
                df_filtered = pd.DataFrame(filtered_tasks, columns=["Title", "Priority", "Status", "Date", "Description"])
                st.dataframe(df_filtered)
            else:
                st.info("No tasks found with the selected priority.")

                
        elif view_option == "Summary by Status":
            summary = task_summary_by_status()
            
            if summary:
                df_summary = pd.DataFrame(summary, columns=["Status", "Count"])
                fig = px.bar(df_summary, x='Status', y='Count', title="Tasks Summary by Status")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tasks summary to display.")


    elif choice == "Update Task":
        st.write("## Update Task")
        task_list = [i[0] for i in view_all_task_titles()]
        selected_task = st.selectbox("Choose a Task to Edit", task_list)

        if selected_task:
            task_data = get_task(selected_task)

            if task_data:
                with st.form(key='update_task_form'):
                    st.write("### Edit Task Details")
                    col1, col2 = st.columns(2)

                    with col1:
                        new_task_title = st.text_input("Task Title", value=task_data[0])
                        new_task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task_data[1]))
                        new_task_due_date = st.date_input("Due Date", value=pd.to_datetime(task_data[3]))

                    with col2:
                        new_task_status = st.selectbox("Status", ["ToDo", "Doing", "Done"], index=["ToDo", "Doing", "Done"].index(task_data[2]))
                        new_task_description = st.text_area("Task Description", value=task_data[4])

                    submit_button = st.form_submit_button(label='Update Task')

                    if submit_button:   
                        if new_task_status == "Done":
                            st.success(f"Completed!: '{new_task_title}'")
                            st.balloons()
                        else:
                            st.success(f"Task updated: '{new_task_title}'")
                        edit_task_data(new_task_title, new_task_priority, new_task_status, new_task_due_date, new_task_description, task_data[0])
                        



    elif choice == "Delete Task":
        st.write("## Delete Task")
        task_list = [i[0] for i in view_all_task_titles()]
        selected_task = st.selectbox("Choose a Task to Delete", task_list)

        if st.button("Delete Task"):
            delete_data(selected_task)
            st.success(f"Deleted Task: '{selected_task}'")




if __name__ == '__main__':
    main()
