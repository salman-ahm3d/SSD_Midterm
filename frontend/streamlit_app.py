import streamlit as st
import requests

API_BASE_URL = "http://backend:8000"

st.title("📡 Telecom Billing System")

menu = st.sidebar.selectbox("Select Operation", ["Create Customer", "View Customers", "Update Customer", "Delete Customer", "Create Bill", "View Bills", "Update Bill", "Delete Bill"])

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

elif menu == "Update Customer":
    st.header("✏️ Update Customer")
    cid = st.number_input("Enter Customer ID to Update", min_value=1)
    name = st.text_input("New Name (leave blank to keep unchanged)")
    phone = st.text_input("New Phone Number (leave blank to keep unchanged)")
    email = st.text_input("New Email (leave blank to keep unchanged)")
    address = st.text_area("New Address (leave blank to keep unchanged)")
    if st.button("Update Customer"):
        payload = {}
        if name: payload["name"] = name
        if phone: payload["phone_number"] = phone
        if email: payload["email"] = email
        if address: payload["address"] = address
        if not payload:
            st.warning("No fields to update.")
        else:
            res = requests.put(f"{API_BASE_URL}/customers/{cid}", json=payload)
            if res.status_code == 200:
                st.success("Customer updated.")
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

elif menu == "Update Bill":
    st.header("✏️ Update Bill")
    bill_id = st.number_input("Enter Bill ID to Update", min_value=1)
    customer_id = st.text_input("New Customer ID (leave blank to keep unchanged)")
    billing_date = st.text_input("New Billing Date (YYYY-MM-DD, leave blank to keep unchanged)")
    due_date = st.text_input("New Due Date (YYYY-MM-DD, leave blank to keep unchanged)")
    amount = st.text_input("New Amount (leave blank to keep unchanged)")
    status = st.selectbox("New Status (leave blank to keep unchanged)", ["", "Paid", "Unpaid", "Overdue"])
    if st.button("Update Bill"):
        payload = {}
        if customer_id: payload["customer_id"] = int(customer_id)
        if billing_date: payload["billing_date"] = billing_date
        if due_date: payload["due_date"] = due_date
        if amount: payload["amount"] = float(amount)
        if status: payload["status"] = status if status else None
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        if not payload:
            st.warning("No fields to update.")
        else:
            res = requests.put(f"{API_BASE_URL}/bills/{bill_id}", json=payload)
            if res.status_code == 200:
                st.success("Bill updated.")
            else:
                st.error(f"Failed: {res.text}")


