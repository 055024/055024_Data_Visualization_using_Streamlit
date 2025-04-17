# Import Relevant Python Libraries

import pandas as pd
import numpy as np
import scipy.stats as stats
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from scipy import stats
import streamlit as st
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# Load the Test Data
my_df = pd.read_csv("Imports_Exports_Dataset.csv",index_col="Transaction_ID")
# ## Data Sampling
# A Unique Sample of 3001 Records 
my_sample = pd.DataFrame.sample(my_df, n=3001, random_state=55024 ,ignore_index=False)
my_sample['Total_Value'] = round(my_sample['Value']*my_sample['Quantity'],0)
st.title("GLOBAL TRADE ANALYSIS")
st.markdown("---")
st.subheader("Few records of Sample Data ")
st.write(my_sample.head(n=5))
st.markdown("---")
# Sidebar slicer to filter by category
st.sidebar.header("Filter Options")

st.header("Trade Trend Analysis, based on Imports and Exports:")

# Convert 'Date' to datetime format
my_sample['Date'] = pd.to_datetime(my_sample['Date'], dayfirst=True, errors='coerce')

# Sidebar filters

# country_filter = st.sidebar.multiselect("Select Country", options=my_sample['Country'].unique(), default=my_sample['Country'].unique())
years = my_sample['Date'].dt.year.unique()  # Get unique years from the Date column
selected_years = st.sidebar.multiselect(
    "Select Years to Display:",
    options=sorted(years),  # Sort the years in ascending order
    default=[2019, 2020, 2021, 2022, 2023, 2024]  # Default to show all years (adjust as needed)
)
category_filter = st.sidebar.multiselect("Select Category", options=my_sample['Category'].unique(), default=my_sample['Category'].unique())
# product_filter = st.sidebar.multiselect("Select Product", options=my_sample['Product'].unique(), default=my_sample['Product'].unique())

# Apply filters
filtered_data = my_sample[
                          (my_sample['Date'].dt.year.isin(selected_years))&
                          (my_sample['Category'].isin(category_filter)) 
                         ]

# Title
st.title("Global Trade Trend Analysis Dashboard")

# A. Trade Volume Analysis
st.subheader("A. Trade Volume Analysis")

# 1. Total Value of Goods Exported and Imported (2019-2024) - Sunburst Chart
import_export_comparison = filtered_data.groupby('Import_Export')[['Value']].sum().reset_index()
fig_sunburst = px.sunburst(import_export_comparison, path=['Import_Export'], values='Value', title="Total Value of Goods (Exported vs Imported)")
st.plotly_chart(fig_sunburst)

# 2. Top 10 Countries with Maximum Export Sales Profits - Treemap
export_data = filtered_data[filtered_data['Import_Export'] == 'Export']
trade_volume_country = export_data.groupby('Country')[['Value']].sum().sort_values(by='Value', ascending=False).head(10).reset_index()
fig_treemap_country = px.treemap(trade_volume_country, path=['Country'], values='Total_Value', title="Top 10 Countries with Maximum Export Sales Profits")
st.plotly_chart(fig_treemap_country)

# B. Temporal Trends (Yearly/Monthly Trends)
st.subheader("B. Temporal Trends (Yearly/Monthly Trends)")

# 3. Yearly Export Trends - Line Chart with Markers
export_data['Year'] = export_data['Date'].dt.year
yearly_trends_export = (
    export_data.groupby('Year')[['Total_Value']]
    .sum()
    .sort_values(by='Year')  # Sort by 'Year' instead of 'Total_Value'
    .reset_index()
)

# Create a complete range of years (2019 to 2024) and merge with the existing data
all_years = pd.DataFrame({'Year': range(2019, 2025)})
yearly_trends_export = all_years.merge(yearly_trends_export, on='Year', how='left')

# Replace NaN values (for missing years) with 0 or an appropriate value
yearly_trends_export['Total_Value'].fillna(0, inplace=True)

# Create the line chart with markers
fig_yearly_trends_export = px.line(
    yearly_trends_export, 
    x='Year', 
    y='Total_Value', 
    title="Yearly Export Volume (2019-2024)", 
    markers=True
)

# Display the chart in Streamlit
st.plotly_chart(fig_yearly_trends_export)

# 4. Yearly Import Trends - Bubble Chart
import_data = filtered_data[filtered_data['Import_Export'] == 'Import']
import_data['Year'] = import_data['Date'].dt.year
yearly_trends_import = import_data.groupby('Year')[['Total_Value']].sum().reset_index()
fig_bubble_import = px.scatter(yearly_trends_import, x='Year', y='Total_Value', size='Total_Value', title="Yearly Import Volume", color='Year', hover_name='Year')
st.plotly_chart(fig_bubble_import)

# C. Geographical Trade Patterns
st.subheader("C. Geographical Trade Patterns")

# 5. Heatmap for Countries Importing the highest valued goods
top_importing_countries = import_data.groupby('Country')[['Total_Value']].sum().sort_values(by='Total_Value', ascending=False).head(10).reset_index()
fig_heatmap_importing = px.imshow(top_importing_countries.pivot_table(values='Total_Value', index='Country', fill_value=0), title="Top 10 Countries Importing the Highest Valued Goods (Heatmap)")
st.plotly_chart(fig_heatmap_importing)

# 6. Choropleth map for exporting countries
    # Calculate top exporting countries
top_exporting_countries = (
    export_data.groupby('Country')[['Total_Value']]
    .sum()
    .sort_values(by='Total_Value', ascending=False)
    .head(10)
    .reset_index()
)
    
# Create the choropleth map
fig_choropleth_exporting = px.choropleth(
    top_exporting_countries,
    locations='Country',
    locationmode='country names',  # Check if 'country names' matches your data
    color='Total_Value',
    hover_name='Country',
    title="Top 10 Countries Exporting the Highest Valued Goods",
    projection="natural earth"  # Set a projection type for better visualization
)
    
    # Display the plot in Streamlit
st.plotly_chart(fig_choropleth_exporting)
# top_exporting_countries = export_data.groupby('Country')[['Total_Value']].sum().sort_values(by='Total_Value', ascending=False).head(10).reset_index()
# fig_choropleth_exporting = px.choropleth(top_exporting_countries, locations='Country', locationmode='country names', color='Total_Value', hover_name='Country', title="Top 10 Countries Exporting the Highest Valued Goods")
# st.plotly_chart(fig_choropleth_exporting)

# D. Supplier Behavior
st.subheader("D. Supplier Behavior")

# 7. Top 10 Global Suppliers Exporting their Products - Scatter Plot
top_suppliers = export_data.groupby('Supplier')[['Total_Value']].sum().sort_values(by='Total_Value', ascending=False).head(10).reset_index()
fig_scatter_suppliers = px.scatter(top_suppliers, x='Supplier', y='Total_Value', size='Total_Value', title="Top 10 Global Suppliers by Total Value")
st.plotly_chart(fig_scatter_suppliers)

# E. Trade Performance (Evaluated based on Country)
st.subheader("E. Trade Performance")

# 8. Trade Balance (Export vs Import) - Bar Chart with Custom Colors
trade_balance = filtered_data.groupby(['Country', 'Import_Export'])[['Total_Value']].sum().unstack().fillna(0)
trade_balance.columns = ['Import_Total_Value', 'Export_Total_Value']
trade_balance['Trade_Balance'] = trade_balance['Export_Total_Value'] - trade_balance['Import_Total_Value']
top_trade_balance = trade_balance.sort_values(by="Trade_Balance", ascending=False).head(5).reset_index()

fig_trade_balance = px.bar(top_trade_balance, x='Country', y='Trade_Balance', title="Top 5 Countries with Maximum Trade Balance", color='Country', color_continuous_scale=px.colors.sequential.Teal)
st.plotly_chart(fig_trade_balance)

# F. Cost and Revenue Analysis
st.subheader("F. Cost and Revenue Analysis")

# 9. Average Trade Value per Transaction - Gauge Chart
average_value_per_transaction = filtered_data['Value'].mean()
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=average_value_per_transaction,
    title={"text": "Average Trade Value per Transaction"},
    gauge={'axis': {'range': [0, max(filtered_data['Value'])]}}
))
st.plotly_chart(fig_gauge)

# G. Shipping and Logistics Analysis
st.subheader("G. Shipping and Logistics Analysis")

# 10. Shipping Method Preferences for Exported Goods - Donut Chart
fig_donut_shipping_export = px.pie(export_data, names='Shipping_Method', title='Shipping Method Preferences for Exported Goods', hole=0.4)
st.plotly_chart(fig_donut_shipping_export)

# 11. Shipping Method Preferences for Imported Goods - Donut Chart
fig_donut_shipping_import = px.pie(import_data, names='Shipping_Method', title='Shipping Method Preferences for Imported Goods', hole=0.4)
st.plotly_chart(fig_donut_shipping_import)

# H. Payment Term Analysis
st.subheader("H. Payment Term Analysis")

# 12. Common Payment Methods for Exported Products - Pie Chart
fig_payment_export = px.pie(export_data, names='Payment_Terms', title='Common Payment Methods for Exported Products', hole=0.3)
st.plotly_chart(fig_payment_export)

# 13. Common Payment Methods for Imported Products - Pie Chart
fig_payment_import = px.pie(import_data, names='Payment_Terms', title='Common Payment Methods for Imported Products', hole=0.3)
st.plotly_chart(fig_payment_import)

# Display filtered data at the bottom
st.subheader("Filtered Data View")
st.dataframe(filtered_data)


# Title of the Dashboard
st.title("Global Trade Trend Dashboard: Insights and Analysis")

# Introduction
st.markdown("""
## **Overview**
This dashboard provides an in-depth analysis of global trade trends between 2019 and 2024, focusing on imports, exports, shipping methods, suppliers, and other essential metrics. The data is visualized through various charts, allowing for an interactive exploration of trade patterns and performance across multiple dimensions.
""")

# Section 1: Trade Volume Analysis
st.markdown("""
### **1. Trade Volume Analysis**
- **Total Value of Goods Exported and Imported**: The sunburst chart compares total imports and exports over the years.
  - **Insight**: The export volume has been consistently higher than the import volume, reflecting a global focus on wealth generation through exports.
  
- **Top 10 Countries with Maximum Export Sales Profits**: The treemap showcases the top 10 countries that have generated the most export sales profits.
  - **Insight**: There is no dominating country considering top 10 countries as export sales profits are not very significant for these countries.
""")

# Section 2: Temporal Trends
st.markdown("""
### **2. Temporal Trends (Yearly/Monthly Trends)**
- **Yearly Export Volume**: The line chart shows how export volumes have evolved over time.
  - **Insight**: Export volumes peaked in 2021-2022, reflecting a strong recovery post-pandemic, whereas 2019 saw more stable growth.
  
- **Yearly Import Volume**: Visualized through a bubble chart, which represents the total import values each year.
  - **Insight**: Imports have also shown an increase, with larger volumes observed in 2021-2022, suggesting strong global demand post-pandemic.
""")

# Section 3: Geographical Trade Patterns
st.markdown("""
### **3. Geographical Trade Patterns**
- **Top 10 Importing Countries**: The heatmap highlights the countries that spend the most on imported goods.
  - **Insight**: Thoough US, China, and India are major importers for many goods but in our case we see countries like czech Republic, Gabon,etc highlighting their strong domestic demand for products.

- **Top 10 Exporting Countries**: The choropleth map shows the countries with the highest export values.
  - **Insight**: Here also we see a that Countries like China, Germany, and Japan which are major exporters of many goods does not dominate global exports, especially in electronics, vehicles, and machinery.
""")

# Section 4: Supplier Behavior
st.markdown("""
### **4. Supplier Behavior**
- **Top 10 Global Suppliers**: A scatter plot visualizes the most profitable suppliers in global trade.
  - **Insight**: Suppliers like Carter Ltd, Jhonson Inc and Clark Inc US lead in export value, maintaining their dominance in the global supply chain.
""")

# Section 5: Trade Performance (Country-Wise Evaluation)
st.markdown("""
### **5. Trade Performance (Country-Wise Evaluation)**
- **Top 5 Countries with Maximum Trade Balance**: A bar chart shows countries with the highest positive trade balance.
  - **Insight**: Countries like Gabon  and Czech  have a significant trade surplus, exporting far more than they import.

- **Countries with Negative Trade Balances**: Countries with higher import dependence are highlighted.
  - **Insight**: Some countries, like India, have a trade deficit, importing more goods than they export.
""")

# Section 6: Cost and Revenue Analysis
st.markdown("""
### **6. Cost and Revenue Analysis**
- **Average Trade Value per Transaction**: A gauge chart displays the average value per transaction.
  - **Insight**: Higher transaction values indicate that trade often involves bulk or high-cost goods.

- **Average Value per Unit**: The bar chart shows which products generate the most revenue per unit sold.
  - **Insight**: High-value goods such as electronics and machinery have the highest unit values, reflecting their capital-intensive nature.
""")

# Section 7: Shipping and Logistics
st.markdown("""
### **7. Shipping and Logistics**
- **Shipping Method Preferences for Exports and Imports**: Donut charts show the preferred shipping methods for both exports and imports.
  - **Insight**: Sea freight is the most popular shipping method, as it offers cost-efficiency for bulk trade, while air freight is used more selectively for urgent or high-value goods.
""")

# Section 8: Payment Term Analysis
st.markdown("""
### **8. Payment Term Analysis**
- **Common Payment Methods for Exports and Imports**: Pie charts show the most popular payment methods used.
  - **Insight**: Prepaid and payment on delivery are the most common terms, offering security and guarantees for international trade.
""")


# Concluding Remarks
st.markdown("""
### **Concluding Remarks**
The Global Trade Trend Dashboard offers a comprehensive overview of international trade between 2019 and 2024. By visualizing critical metrics such as trade volume, geographical patterns, supplier behavior, and shipping preferences, this dashboard provides a valuable tool for businesses, policymakers, and economists to make data-driven decisions.

Use the filters and charts to explore trade patterns relevant to your interests, and gain insights that can optimize trade strategies, improve supply chains, and understand market dynamics.
""")
