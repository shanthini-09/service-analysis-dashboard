import pandas as pd
import plotly.express as px
import streamlit as st

# Dictionary of important dates for 2024
important_dates = {
    "New Year": "2024-01-01",
    "Pongal": "2024-01-14",
    "Republic Day": "2024-01-26",
    "Good Friday": "2024-03-29",
    "Eid al-Fitr": "2024-04-10",
    "Tamil New Year": "2024-04-14",
    "Eid al-Adha": "2024-06-16",
    "Independence Day": "2024-08-15",
    "Diwali": "2024-11-01",
    "Christmas": "2024-12-25",
    "Exam Start": "2024-03-01",
    "Exam End": "2024-04-15",
    "Wedding Peak 1": "2024-02-15",
    "Wedding Peak 2": "2024-11-25"
}

# Streamlit page configuration
st.set_page_config(page_title="Service and Leave Data Analysis", layout="wide")
st.title("Service Sales and Leave Data Analysis for 2024 Events")

# Sidebar file upload for both datasets
st.sidebar.header("Upload Your Datasets")
sales_file = st.sidebar.file_uploader("Upload Service Sales CSV", type=["csv"])
leaves_file = st.sidebar.file_uploader("Upload Leaves Data CSV", type=["csv"])

# Helper function to load data
@st.cache_data
def load_data(file, date_column=None, numeric_columns=None):
    try:
        data = pd.read_csv(file, low_memory=False)
        # Convert date column to datetime
        if date_column:
            data[date_column] = pd.to_datetime(data[date_column], errors='coerce', dayfirst=True)
        # Convert specified numeric columns to numeric
        if numeric_columns:
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        # Drop rows with invalid date or numeric values
        if date_column:
            data = data.dropna(subset=[date_column])
        if numeric_columns:
            data = data.dropna(subset=numeric_columns)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load sales and leaves datasets
sales_data = load_data(sales_file, date_column="Sale Date", numeric_columns=["Sales Collected (Exc.Tax)"]) if sales_file else None
leaves_data = load_data(leaves_file, date_column="Date", numeric_columns=["MTD Sale"]) if leaves_file else None

# Check if data is loaded
if sales_data is None or sales_data.empty:
    st.warning("Please upload a valid Service Sales dataset.")
else:
    st.write("Sales Data Preview:")
    st.dataframe(sales_data)

if leaves_data is None or leaves_data.empty:
    st.warning("Please upload a valid Leaves dataset.")
else:
    st.write("Leaves Data Preview:")
    st.dataframe(leaves_data)

# Proceed only if both datasets are loaded
if sales_data is not None and not sales_data.empty and leaves_data is not None and not leaves_data.empty:
    # Filter sales data for 2024
    sales_data['Year'] = sales_data['Sale Date'].dt.year
    filtered_sales = sales_data[sales_data['Year'] == 2024]

    # Dropdown for event selection from sales and leaves datasets
    st.subheader("Event Selection")
    selected_event = st.selectbox("Choose an event:", list(important_dates.keys()))
    event_date = pd.to_datetime(important_dates[selected_event])

    # Filter sales data for the selected event (±7 days)
    event_sales = filtered_sales[
        (filtered_sales['Sale Date'] >= event_date - pd.Timedelta(days=7)) &
        (filtered_sales['Sale Date'] <= event_date + pd.Timedelta(days=7))
    ]

    # Dropdown for center selection in sales data
    selected_center = st.selectbox("Choose a Center:", 
                                   filtered_sales['Center Name'].unique() if 'Center Name' in filtered_sales.columns else ["All Centers"])

    if selected_center != "All Centers":
        event_sales = event_sales[event_sales['Center Name'] == selected_center]

    # Filter leaves data for the selected event
    event_leaves = leaves_data[
        (leaves_data['Date'] >= event_date - pd.Timedelta(days=7)) &
        (leaves_data['Date'] <= event_date + pd.Timedelta(days=7))
    ]

    # Display filtered data
    if not event_sales.empty or not event_leaves.empty:
        st.subheader(f"Filtered Data for {selected_event} (±7 Days from {event_date.strftime('%Y-%m-%d')})")

        if not event_sales.empty:
            st.write("Sales Data:")
            st.dataframe(event_sales)

            # Plot MTD Sales Histogram for Sales Data
            sales_mtd = event_sales.groupby('Sale Date', as_index=False)['Sales Collected (Exc.Tax)'].sum()
            fig_sales = px.bar(
                sales_mtd, x='Sale Date', y='Sales Collected (Exc.Tax)',
                color='Sales Collected (Exc.Tax)', color_continuous_scale="blues",
                title=f"Sales MTD Histogram Around {selected_event}"
            )
            fig_sales.update_layout(
                xaxis_title="Date", yaxis_title="MTD Sales (Exc. Tax)", bargap=0.2
            )
            st.plotly_chart(fig_sales)

            # Total Sales Analysis
            total_sales = event_sales['Sales Collected (Exc.Tax)'].sum()
            st.subheader("Total Sales Analysis")
            st.write(f"Total Sales for {selected_center} during {selected_event}: {total_sales:.2f}")
        else:
            st.warning(f"No sales data found for {selected_event} (±7 days).")

        if not event_leaves.empty:
            st.write("Leaves Data:")
            st.dataframe(event_leaves)

            # Plot MTD Sales Histogram for Leaves Data
            leaves_mtd = event_leaves.groupby('Date', as_index=False)['MTD Sale'].sum()
            fig_leaves = px.bar(
                leaves_mtd, x='Date', y='MTD Sale',
                color='MTD Sale', color_continuous_scale="greens",
                title=f"Leave MTD Histogram Around {selected_event}"
            )
            fig_leaves.update_layout(
                xaxis_title="Date", yaxis_title="MTD Sales (Leave Data)", bargap=0.2
            )
            st.plotly_chart(fig_leaves)

            # Total Leave Sales Analysis
            total_leaves_sales = event_leaves['MTD Sale'].sum()
            st.subheader("Total Leave Sales Analysis")
            st.write(f"Total Leave Sales during {selected_event}: {total_leaves_sales:.2f}")
        else:
            st.warning(f"No leave data found for {selected_event} (±7 days).")
