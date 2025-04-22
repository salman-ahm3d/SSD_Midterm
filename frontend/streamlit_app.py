import streamlit as st
import requests

API_BASE_URL = "http://backend:8000"

st.title("📡 Telecom Billing System")

menu = st.sidebar.selectbox("Select Operation", ["Create Customer", "View Customers", "Delete Customer", "Create Bill", "View Bills", "Delete Bill"])

# ------------------ CUSTOMER ------------------

if menu == "Create Customer":
    st.header("➕ Add New Customer")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    address = st.text_area("Address")
    if st.button("Create"):
        payload = {
            "name": name,
            "phone_number": phone,
            "email": email,
            "address": address
        }
        res = requests.post(f"{API_BASE_URL}/customers/", json=payload)
        if res.status_code == 200:
            st.success("Customer created!")
        else:
            st.error(f"Failed: {res.text}")

elif menu == "View Customers":
    st.header("📋 Customer List")
    res = requests.get(f"{API_BASE_URL}/customers/")
    if res.status_code == 200:
        customers = res.json()
        for c in customers:
            st.write(f"🧑 {c['customer_id']}: {c['name']} | {c['phone_number']} | {c['email']}")

elif menu == "Delete Customer":
    st.header("❌ Delete Customer")
    cid = st.number_input("Enter Customer ID", min_value=1)
    if st.button("Delete"):
        res = requests.delete(f"{API_BASE_URL}/customers/{cid}")
        if res.status_code == 200:
            st.success("Customer deleted.")
        else:
            st.error(f"Failed: {res.text}")

# ------------------ BILL ------------------

elif menu == "Create Bill":
    st.header("🧾 Generate Bill")
    customer_id = st.number_input("Customer ID", min_value=1)
    billing_date = st.date_input("Billing Date")
    due_date = st.date_input("Due Date")
    amount = st.number_input("Amount", min_value=0.0)
    status = st.selectbox("Status", ["Paid", "Unpaid", "Overdue"])
    if st.button("Create Bill"):
        payload = {
            "customer_id": customer_id,
            "billing_date": str(billing_date),
            "due_date": str(due_date),
            "amount": amount,
            "status": status
        }
        res = requests.post(f"{API_BASE_URL}/bills/", json=payload)
        if res.status_code == 200:
            st.success("Bill created.")
        else:
            st.error(f"Failed: {res.text}")

elif menu == "View Bills":
    st.header("📃 All Bills")
    res = requests.get(f"{API_BASE_URL}/bills/")
    if res.status_code == 200:
        bills = res.json()
        for b in bills:
            st.write(f"💵 Bill #{b['bill_id']} | Customer #{b['customer_id']} | {b['billing_date']} - ₹{b['amount']} ({b['status']})")

elif menu == "Delete Bill":
    st.header("🗑️ Delete Bill")
    bill_id = st.number_input("Enter Bill ID", min_value=1)
    if st.button("Delete"):
        res = requests.delete(f"{API_BASE_URL}/bills/{bill_id}")
        if res.status_code == 200:
            st.success("Bill deleted.")
        else:
            st.error(f"Failed: {res.text}")

