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
st.title("Hubspot Data Analysis!!")

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
    1. Clean and summarize the data
    2. Show meaningful insights and statistics
    3. Create comprehensive visualizations for all the columns in [column_info]. Use a variety of chart types (e.g., bar, line, pie, scatter) to cover all possible aspects and relationships between the data columns. Ensure the visualizations and insights are clear, informative, and well-labeled to support data understanding and decision-making.
    4. Display results using Streamlit widgets

    Make sure the code assumes a DataFrame named 'df' is already defined.
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

