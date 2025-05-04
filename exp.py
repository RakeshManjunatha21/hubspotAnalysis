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
st.title("Hubspot Data Analysis!!!")

uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # Show column metadata
    st.subheader("🧾 Column Metadata")
    column_info = "\n".join([f"- **{col}**: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
    st.markdown(column_info)

    # Create prompt for Gemini
    prompt = f"""
    I have uploaded an Excel file with the following columns and data types:
    {column_info}
     
    Generate Python code using pandas, matplotlib, seaborn, and Streamlit to:
    1. Clean the entire dataset, including handling missing (NaN) values.
    2. Generate a comprehensive and intelligent summary for all columns (both categorical and numerical) — on a high level information needed for business people
    3. Analyze each column's data and create the most appropriate visualization (give plotly visualization) dynamically. Choose the best-suited chart type for each column without applying fixed filters (e.g., for categorical data use bar or pie charts, for numerical data use histograms, line charts, or scatter plots as appropriate).
    4. Ensure every column is processed and visualized.
    5. Display the summary and visualizations clearly using Streamlit components in an organized layout.
     
    Make sure the code assumes a DataFrame named 'df' is already defined and uses no hard-coded filters.
    """

    st.subheader("🤖 Generating Code...")
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

