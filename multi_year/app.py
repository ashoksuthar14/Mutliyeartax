import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to load the tax filing dataset from the CSV file
def load_tax_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Function to get filings for a specific user
def get_user_filings(df, user_id):
    return df[df['user_id'] == user_id]

# Function to apply filters to the dataset
def apply_filters(df, year=None, income_range=None, status=None):
    if year:
        df = df[df['year'] == year]
    if income_range:
        df = df[(df['income'] >= income_range[0]) & (df['income'] <= income_range[1])]
    if status:
        df = df[df['status'] == status]
    return df

# Load the dataset
file_path = 'data/tax_filings_dataset.csv'
df = load_tax_data(file_path)

# User input to select their user ID
st.title("Multi-Year Tax Filing Portal")
user_id = st.number_input("Enter your User ID:", min_value=1, max_value=100)

# Fetch and display past filings for the user
if user_id:
    user_filings = get_user_filings(df, user_id)
    
    if not user_filings.empty:
        st.write(f"Displaying tax filings for User ID: {user_id}")
        st.dataframe(user_filings)

        # Filter options
        st.sidebar.header("Filter Options")
        selected_year = st.sidebar.selectbox("Select Year:", options=[None] + sorted(user_filings['year'].unique().tolist()))
        income_range = st.sidebar.slider("Income Range:", 
                                         min_value=float(user_filings['income'].min()), 
                                         max_value=float(user_filings['income'].max()), 
                                         value=(float(user_filings['income'].min()), float(user_filings['income'].max())))
        selected_status = st.sidebar.selectbox("Filing Status:", options=[None] + user_filings['status'].unique().tolist())
        
        # Apply filters
        filtered_data = apply_filters(user_filings, year=selected_year, income_range=income_range, status=selected_status)
        
        st.write("Filtered Data:")
        st.dataframe(filtered_data)

        # Data visualization - Total Income, Deductions, Tax Paid, and Refund
        st.subheader("Tax Data Visualization")

        st.write("### Total Income and Deductions")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='year', y='income', data=filtered_data, ax=ax, label='Total Income')
        sns.barplot(x='year', y='deductions', data=filtered_data, ax=ax, label='Deductions', color='orange')
        ax.set_ylabel("Amount (₹)")
        ax.set_title("Total Income vs Deductions Over the Years")
        st.pyplot(fig)

        st.write("### Tax Paid and Refund")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='year', y='tax_paid', data=filtered_data, ax=ax, label='Tax Paid', color='green')
        sns.barplot(x='year', y='refund', data=filtered_data, ax=ax, label='Refund', color='red')
        ax.set_ylabel("Amount (₹)")
        ax.set_title("Tax Paid vs Refund Over the Years")
        st.pyplot(fig)

        # Pie chart for filing status distribution
        st.write("### Filing Status Distribution")
        fig, ax = plt.subplots()
        status_counts = filtered_data['status'].value_counts()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightblue', 'lightgreen', 'lightcoral'])
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

        # Line chart for Income and Refunds Over the Years
        st.write("### Income and Refund Over the Years")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='year', y='income', data=filtered_data, ax=ax, label='Total Income', marker="o")
        sns.lineplot(x='year', y='refund', data=filtered_data, ax=ax, label='Refund', marker="o", color='red')
        ax.set_ylabel("Amount (₹)")
        ax.set_title("Total Income and Refund Trend Over the Years")
        st.pyplot(fig)

        # Amend Filings
        st.subheader("Amend Tax Filing")
        selected_year_to_amend = st.selectbox("Select a year to amend:", user_filings['year'].unique())
        
        if selected_year_to_amend:
            filing_to_amend = user_filings[user_filings['year'] == selected_year_to_amend].iloc[0]
            
            # Editable fields for amendment
            income = st.number_input("Income", value=filing_to_amend['income'])
            deductions = st.number_input("Deductions", value=filing_to_amend['deductions'])
            tax_paid = st.number_input("Tax Paid", value=filing_to_amend['tax_paid'])
            
            # Recalculate refund and taxable income
            taxable_income = income - deductions
            refund = max(0, tax_paid - (taxable_income * 0.2))
            
            st.write(f"Calculated Taxable Income: ₹{taxable_income}")
            st.write(f"Calculated Refund: ₹{refund}")
            
            # Submit amendments
            if st.button("Submit Amendment"):
                df.loc[(df['user_id'] == user_id) & (df['year'] == selected_year_to_amend), ['income', 'deductions', 'taxable_income', 'tax_paid', 'refund']] = [income, deductions, taxable_income, tax_paid, refund]
                st.success(f"Amended filing for the year {selected_year_to_amend} successfully submitted!")

    # Allow the user to start a new filing for the current year
    if st.button("Start New Filing for 2023"):
        # Get the most recent year filing for the user
        most_recent_filing = user_filings.sort_values('year', ascending=False).iloc[0]
        
        # Carry over data
        st.write("Carrying over data from the previous year's filing.")
        income_2023 = st.number_input("Income for 2023", value=most_recent_filing['income'])
        deductions_2023 = st.number_input("Deductions for 2023", value=most_recent_filing['deductions'])
        
        taxable_income_2023 = income_2023 - deductions_2023
        tax_paid_2023 = st.number_input("Tax Paid for 2023", value=most_recent_filing['tax_paid'])
        
        refund_2023 = max(0, tax_paid_2023 - (taxable_income_2023 * 0.2))
        
        st.write(f"Calculated Taxable Income for 2023: ₹{taxable_income_2023}")
        st.write(f"Calculated Refund for 2023: ₹{refund_2023}")
        
        if st.button("Submit Filing for 2023"):
            # Append new filing to the DataFrame (in real applications, save to database)
            new_filing = {
                'id': df['id'].max() + 1,
                'user_id': user_id,
                'year': 2023,
                'income': income_2023,
                'deductions': deductions_2023,
                'taxable_income': taxable_income_2023,
                'tax_paid': tax_paid_2023,
                'refund': refund_2023,
                'filing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'filed'
            }
            df = df.append(new_filing, ignore_index=True)
            st.success("2023 filing submitted successfully!")
    
    # Save the DataFrame back to CSV
    if st.button("Save Changes"):
        df.to_csv(file_path, index=False)
        st.success("Changes saved to the dataset!")

else:
    st.write("Please enter your User ID to view your tax filings.")
