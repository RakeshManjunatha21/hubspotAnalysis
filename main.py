import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import re

# Set Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBIBr01u6_BNVfYk989DXkv3FKQA928Kq8"  # Replace with your key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

# Function to extract code from Markdown block
def extract_code(response_text):
    match = re.search(r"```(?:python)?\n(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()  # fallback if no triple backticks

# Streamlit UI
st.set_page_config(page_title="Smart Excel Analyzer", layout="wide")
st.title("📊 Data Analysis Hubspot Paperflite")

uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # Show column metadata
    st.subheader("🧾 Column Metadata")
    column_info = "\n".join([f"- **{col}**: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
    st.markdown(column_info)

    # Create prompt for Gemini - updated to remove filters and do intelligent analysis.
    prompt = f"""
    I have uploaded an Excel file with the following columns and data types:
    {column_info}
    
    Generate Python code using pandas, matplotlib, seaborn, plotly, and Streamlit that:
    
    1. Cleansing & Preprocessing
    Cleans the entire dataset:
    
    Handles missing values using appropriate strategies (drop, fill, or flag based on column type and missing ratio).
    
    Detects and treats outliers for numerical columns using statistical methods (e.g., IQR, Z-score).
    
    Converts data types as needed (e.g., dates to datetime, numeric strings to float/int).
    
    Encodes categorical variables for analysis where needed (label/one-hot encoding only if required for specific visualizations).
    
    2. Comprehensive Intelligent Summary
    Generates a high-level summary suitable for business users:
    
    Column name, type, number of missing values, % of missing, unique values count, top frequent values.
    
    For numerical columns: mean, median, std, min, max, skewness, kurtosis.
    
    For categorical/text columns: mode, frequency distribution, unique count, entropy.
    
    For datetime columns: time range, granularity, and temporal trends.
    
    3. Deep-Dive Per-Column Analysis with Smart Visualization
    Analyzes every column in depth, using dynamic logic to choose the best chart for each type:
    
    Numerical Columns:
    
    Histogram (distribution)
    
    Boxplot (outliers)
    
    Scatterplot (with other numerical columns)
    
    Line plots (if datetime available)
    
    KDE plots (for density)
    
    Categorical Columns:
    
    Bar chart (frequency)
    
    Pie chart (share)
    
    Countplot (Seaborn)
    
    Datetime Columns:
    
    Time series line charts
    
    Aggregated bar plots (by month, year)
    
    Heatmaps of activity (if timestamps)
    
    Mixed (e.g., category vs numeric):
    
    Boxplot, violin plot (category vs numeric)
    
    Grouped bar plots (aggregates)
    
    Use plotly.express for all interactive visualizations (e.g., px.histogram, px.box, px.scatter, px.line, px.pie, px.bar, etc.)
    
    4. Extensive Visualization Coverage
    Ensures every column is visualized in multiple relevant ways, not just one.
    
    Automatically generates:
    
    At least 2-3 relevant plots per column
    
    Additional multi-column plots if there are clear relationships (e.g., correlation heatmap, pairplot)
    
    Avoids hard-coded filters — uses data-driven logic (e.g., cardinality of categorical columns, dtype detection)
    
    5. Streamlit App Design
    Presents everything in an interactive Streamlit dashboard:
    
    Tabs or expanders for:
    
    Data Cleaning Summary
    
    Column-Wise Summaries
    
    Individual Column Visualizations
    
    Correlation & Advanced Multi-variable Visuals
    
    Streamlit st.sidebar to filter/select column or analysis type dynamically
    
    Uses Streamlit's layout features (columns, expander, tabs) for clear, business-friendly presentation
    """

    st.subheader("Generating Code...")
    try:
        response = model.generate_content(prompt)
        raw_response = response.text
        generated_code = extract_code(raw_response)

        with st.expander("🔍 View Generated Code"):
            st.code(generated_code, language="python")

        st.subheader("📈 Running Analysis...")
        exec_namespace = {"st": st, "pd": pd, "df": df}

        # Optional basic safety check
        forbidden_keywords = ["os.", "open(", "eval(", "exec(", "subprocess"]
        if any(keyword in generated_code for keyword in forbidden_keywords):
            st.error("⚠️ Unsafe code detected. Execution aborted.")
        else:
            exec(generated_code, exec_namespace)

    except Exception as e:
        st.error(f"⚠️ Error during code generation or execution: {e}")
