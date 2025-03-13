import streamlit as st
import pandas as pd
import ollama  # For local LLM processing

st.title("Transaction Categorizer with Local LLM")

# Upload files
categories_file = st.file_uploader(
    "Upload Categories File (Excel)", type=["xls", "xlsx"]
)
transactions_file = st.file_uploader(
    "Upload Transactions File (Excel)", type=["xls", "xlsx"]
)

if categories_file and transactions_file:
    # Load data
    categories_df = pd.read_excel(categories_file)
    transactions_df = pd.read_excel(transactions_file)

    st.write("### Transaction Categories")
    st.dataframe(categories_df)

    st.write("### Transactions")
    st.dataframe(transactions_df.head())

    # Ensure category column exists
    category_list = categories_df.iloc[:, 0].tolist()  # First column as category names

    # Prepare prompt
    transactions_text = "\n".join(
        transactions_df.iloc[:, 0].astype(str).tolist()
    )  # First column as transactions
    prompt = f"""
    You are an AI trained to classify financial transactions into categories. 
    The available categories are: {', '.join(category_list)}.
    
    Classify the following transactions into one of the categories:
    {transactions_text}
    
    Return the response as a JSON list of dictionaries with 'transaction' and 'category'.
    """

    # Run LLM classification
    response = ollama.chat(
        model="mistral", messages=[{"role": "user", "content": prompt}]
    )

    # Extract response (assuming valid JSON output)
    import json

    try:
        categorized_transactions = json.loads(response["message"]["content"])
        categorized_df = pd.DataFrame(categorized_transactions)
        st.write("### Categorized Transactions")
        st.dataframe(categorized_df)

        # Download button
        st.download_button(
            "Download Categorized Transactions",
            categorized_df.to_csv(index=False),
            file_name="categorized_transactions.csv",
            mime="text/csv",
        )
    except:
        st.error("LLM response could not be processed. Check model output.")
