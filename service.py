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
st.set_page_config(page_title="Service Data Event Analysis", layout="wide")
st.title("Service Data Analysis for 2024 Events")

# Sidebar file upload
st.sidebar.header("Upload Your Service Sales Data")
uploaded_file = st.sidebar.file_uploader("Upload Service Sales CSV", type=["csv"])

# Helper function to load data
@st.cache_data
def load_data(file):
    try:
        data = pd.read_csv(file, low_memory=False)
        # Convert 'Sale Date' to datetime
        data['Sale Date'] = pd.to_datetime(data['Sale Date'], errors='coerce', dayfirst=True)
        # Convert sales column to numeric
        if 'Sales Collected (Exc.Tax)' in data.columns:
            data['Sales Collected (Exc.Tax)'] = pd.to_numeric(data['Sales Collected (Exc.Tax)'], errors='coerce')
        return data.dropna(subset=['Sale Date', 'Sales Collected (Exc.Tax)'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

if uploaded_file:
    # Load dataset
    data = load_data(uploaded_file)
    
    if data is not None:
        # Filter for 2024
        data['Year'] = data['Sale Date'].dt.year
        filtered_data = data[data['Year'] == 2024]

        if not filtered_data.empty:
            # Dropdown for event and center selection
            st.subheader("Event and Center Selection")
            selected_event = st.selectbox("Choose an event:", list(important_dates.keys()))
            selected_center = st.selectbox("Choose a Center:", filtered_data['Center Name'].unique() if 'Center Name' in filtered_data.columns else ["All Centers"])

            # Filter data for selected event (±7 days)
            event_date = pd.to_datetime(important_dates[selected_event])
            event_data = filtered_data[
                (filtered_data['Sale Date'] >= event_date - pd.Timedelta(days=7)) & 
                (filtered_data['Sale Date'] <= event_date + pd.Timedelta(days=7))
            ]

            if selected_center != "All Centers":
                event_data = event_data[event_data['Center Name'] == selected_center]

            if not event_data.empty:
                # Display filtered data
                st.subheader(f"Filtered Data for {selected_event} (±7 Days from {event_date.strftime('%Y-%m-%d')})")
                st.dataframe(event_data)

                # Plot MTD Sales Histogram
                mtd_sales = event_data.groupby('Sale Date', as_index=False)['Sales Collected (Exc.Tax)'].sum()
                fig = px.bar(
                    mtd_sales, x='Sale Date', y='Sales Collected (Exc.Tax)',
                    color='Sales Collected (Exc.Tax)', color_continuous_scale="blues",
                    title=f"MTD Sales Histogram Around {selected_event}"
                )
                fig.update_layout(
                    xaxis_title="Date", yaxis_title="MTD Sales (Exc. Tax)",
                    bargap=0.2, xaxis={'categoryorder': 'category ascending'}
                )
                st.plotly_chart(fig)

                # Total Sales
                total_sales = event_data['Sales Collected (Exc.Tax)'].sum()
                st.subheader("Total Sales Analysis")
                st.write(f"Total Sales for {selected_center} during {selected_event}: {total_sales:.2f}")

            else:
                st.warning(f"No sales data found for {selected_event} (±7 days).")
else:
    st.warning("Please upload the service sales dataset.")
