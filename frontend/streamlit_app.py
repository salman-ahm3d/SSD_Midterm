import streamlit as st
import requests
from datetime import date
import json

# API configuration
API_BASE_URL = "http://backend:8000"  # Docker-compose service name
# For local testing without Docker: "http://localhost:8000"

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'role' not in st.session_state:
    st.session_state.role = None

# Helper functions
def make_authenticated_request(endpoint, method="GET", json_data=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = None  # Initialize response variable
    
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=json_data, headers=headers)
        elif method == "PUT":
            response = requests.put(f"{API_BASE_URL}{endpoint}", json=json_data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=headers)
        
        if response is not None:  # Check if response exists
            response.raise_for_status()
            return response.json()
        else:
            st.error("Invalid request method")
            return None
            
    except requests.exceptions.HTTPError as e:
        if response and response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.token = None
            st.rerun()
        error_msg = e.response.text if hasattr(e, 'response') else str(e)
        st.error(f"API Error: {error_msg}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return None

# Authentication
def login(username, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={
                "username": username,
                "password": password,
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            
            # Get user info after successful login
            user_info = make_authenticated_request("/users/me")
            if user_info:
                st.session_state.role = user_info["role"]
                st.session_state.username = user_info["username"]
                return True
        st.error("Login failed. Check your credentials.")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False



# UI Components
def login_form():
    with st.form("Login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if login(username, password):
                st.rerun()

def logout_button():
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.rerun()

# Main App Pages
def dashboard_page():
    st.title("Telecom Billing Dashboard")
    logout_button()
    
    # Display user role
    st.sidebar.write(f"Logged in as: {st.session_state.role.upper()}")

    # Customer Management
    st.header("Customer Management")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Add New Customer"):
            with st.form("add_customer"):
                name = st.text_input("Full Name")
                phone = st.text_input("Phone Number")
                email = st.text_input("Email")
                address = st.text_area("Address")
                if st.form_submit_button("Submit"):
                    customer_data = {
                        "name": name,
                        "phone_number": phone,
                        "email": email,
                        "address": address
                    }
                    result = make_authenticated_request("/customers/", "POST", customer_data)
                    if result and not isinstance(result, str):  # Success case
                        st.success("Customer added successfully!")
                        st.rerun()
                    elif isinstance(result, str):  # Error case
                        st.error(result)

    with col2:
        customers = make_authenticated_request("/customers/")
        if customers:
            st.write("### Existing Customers")
            for customer in customers:
                with st.expander(f"{customer['name']} ({customer['phone_number']})"):
                    st.write(f"**Email:** {customer['email']}")
                    st.write(f"**Address:** {customer['address']}")
                    if st.session_state.role == "admin":
                        # Update Customer Form
                        with st.form(f"update_customer_{customer['customer_id']}"):
                            new_name = st.text_input("Name", value=customer['name'])
                            new_phone = st.text_input("Phone", value=customer['phone_number'])
                            new_email = st.text_input("Email", value=customer['email'])
                            new_address = st.text_area("Address", value=customer['address'])
                            
                            if st.form_submit_button("Update Customer"):
                                update_data = {
                                    "name": new_name,
                                    "phone_number": new_phone,
                                    "email": new_email,
                                    "address": new_address
                                }
                                result = make_authenticated_request(
                                    f"/customers/{customer['customer_id']}",
                                    "PUT",
                                    update_data
                                )
                                if result:
                                    st.success("Customer updated successfully!")
                                    st.rerun()
                    
                    if st.session_state.role == "admin":
                        if st.button(f"Delete {customer['customer_id']}"):
                            make_authenticated_request(
                                f"/customers/{customer['customer_id']}",
                                "DELETE"
                            )
                            st.rerun()
     # Billing Management
    st.header("Billing Management")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Create New Bill"):
            if customers:
                customer_options = {c['customer_id']: f"{c['name']} ({c['phone_number']})" 
                                    for c in customers}
                selected_customer = st.selectbox(
                    "Customer", 
                    options=list(customer_options.keys()), 
                    format_func=lambda x: customer_options[x]
                )
                billing_date = st.date_input("Billing Date", date.today())
                due_date = st.date_input("Due Date", date.today())
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                status = st.selectbox("Status", ["paid", "unpaid", "overdue"])
                
                if st.button("Create Bill"):
                    bill_data = {
                        "customer_id": selected_customer,
                        "billing_date": str(billing_date),
                        "due_date": str(due_date),
                        "amount": float(amount),
                        "status": status
                    }
                    result = make_authenticated_request("/bills/", "POST", bill_data)
                    if result:
                        st.success("Bill created successfully!")
                        st.rerun()
            else:
                st.warning("No customers available. Please add customers first.")

    with col2:
        bills = make_authenticated_request("/bills/")
        if bills:
            st.write("### Recent Bills")
            for bill in bills:
                customer = next((c for c in customers if c['customer_id'] == bill['customer_id']), None)
                cust_name = customer['name'] if customer else "Unknown"
                
                with st.expander(f"Bill #{bill['bill_id']} - {cust_name}: ${bill['amount']} ({bill['status']})"):
                    st.write(f"**Billing Date:** {bill['billing_date']}")
                    st.write(f"**Due Date:** {bill['due_date']}")
                    st.write(f"**Amount:** ${bill['amount']}")
                    st.write(f"**Status:** {bill['status']}")
                    if st.session_state.role == "admin":
                        # Update Bill Form
                        with st.form(f"update_bill_{bill['bill_id']}"):
                            new_customer = st.selectbox(
                                "Customer",
                                options=[c['customer_id'] for c in customers],
                                index=[c['customer_id'] for c in customers].index(bill['customer_id']),
                                format_func=lambda x: next(c['name'] for c in customers if c['customer_id'] == x)
                            )
                            new_billing_date = st.date_input(
                                "Billing Date", 
                                value=date.fromisoformat(bill['billing_date'])
                            )
                            new_due_date = st.date_input(
                                "Due Date", 
                                value=date.fromisoformat(bill['due_date'])
                            )
                            new_amount = st.number_input(
                                "Amount", 
                                value=float(bill['amount']),
                                min_value=0.01,
                                step=0.01
                            )
                            new_status = st.selectbox(
                                "Status",
                                ["paid", "unpaid", "overdue"],
                                index=["paid", "unpaid", "overdue"].index(bill['status'])
                            )
                            
                            if st.form_submit_button("Update Bill"):
                                update_data = {
                                    "customer_id": new_customer,
                                    "billing_date": str(new_billing_date),
                                    "due_date": str(new_due_date),
                                    "amount": new_amount,
                                    "status": new_status
                                }
                                result = make_authenticated_request(
                                    f"/bills/{bill['bill_id']}",
                                    "PUT",
                                    update_data
                                )
                                if result:
                                    st.success("Bill updated successfully!")
                                    st.rerun()
                    
                    if st.session_state.role == "admin":
                        if st.button(f"Delete Bill {bill['bill_id']}"):
                            make_authenticated_request(
                                f"/bills/{bill['bill_id']}",
                                "DELETE"
                            )
                            st.rerun()
                            
    # User Management (Admin only)
    if st.session_state.role == "admin":
        st.header("User Management")
        with st.expander("Add New Operator"):
            with st.form("add_user"):
                username = st.text_input("Operator Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Create Operator"):
                    user_data = {
                        "username": username,
                        "password": password,
                        "role": "operator"
                    }
                    result = make_authenticated_request("/users/", "POST", user_data)
                    if result:
                        st.success("Operator account created!")

# Main App Flow
def main():
    if st.session_state.token is None:
        st.title("Telecom Billing Login")
        login_form()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
