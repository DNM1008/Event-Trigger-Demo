"""
import necessary modules:
    json to parse responses from the llm
    streamlit for the app
    pandas to work with tables/excel files
    ollama for llm processing
"""

import json
import streamlit as st
import pandas as pd
import ollama  # For local LLM processing


def load_abbreviation_dict(file_path):
    """
    Reads abbreviation_dict.xlsx and creates a mapping of abbreviations to the
    full words

    Args:
        file_path (str): path to abbreviation_dict.xlsx

    Returns:
        abbreviation_map (dict): dictionary that maps the abbreviations to their
        full words.
    """
    df = pd.read_excel(file_path)
    abbreviation_map = {}
    for _, row in df.iterrows():
        full_word = row["Full_words"]
        abbreviations = row["Abbreviation"].split(", ")
        for abbr in abbreviations:
            if abbr in abbreviation_map:
                abbreviation_map[abbr].append(full_word)
            else:
                abbreviation_map[abbr] = [full_word]
    return abbreviation_map


def resolve_abbreviation_with_llm(abbreviation, context, possible_words):
    """
    Use LLM to match the abbreviations in the remark to possible full words
    given the context.

    Args:
        abbreviation (str): the abbreviation inside the remark
        context (list of str): the words around the abbreviation, could be used
        to determine what the abbreviation stands for
        possible_words (list of str): possible words that the abbreviation could
        stand for

    Returns:
        (str): the full word that the abbreviation is most likely to
        stand for

    """
    # prompt = f"""
    # You are an AI that resolves abbreviations in financial transactions. Given the context:
    # 
    # Transaction: "{context}"
    # 
    # The abbreviation "{abbreviation}" could mean one of the following: {', '.join(possible_words)}.
    # 
    # Which meaning is most appropriate? Reply with only the best matching word.
    # """

    # Prepare prompt in Vietnamese
    prompt = f"""
    Bạn là một AI có nhiệm vụ giải thích các từ viết tắt trong giao dịch tài chính. Dưới đây là ngữ cảnh:
    
    Giao dịch: "{context}"
    
    Từ viết tắt "{abbreviation}" có thể mang một trong các nghĩa sau: {', '.join(possible_words)}.
    
    Nghĩa nào phù hợp nhất? Hãy trả lời chỉ bằng từ đúng nhất.
    """
    response = ollama.chat(
        model="mistral", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def expand_abbreviations(text, abbreviation_map):
    """
    Replaces the abbreviation with the full word.
    This function finds the abbreviations in a text (remark), then replaces it
    with the most appropriate full words.

    Args:
        text (str): remark
        abbreviation_map (dict): dictionary that defines what the abbreviations
        could stand for

    Returns:
        (str): the text that have had its abbreviations replaced by the full
        words
    """
    words = text.split()
    expanded_words = []
    for word in words:
        if word in abbreviation_map:
            possible_words = abbreviation_map[word]
            if len(possible_words) == 1:
                expanded_words.append(possible_words[0])
            else:
                expanded_words.append(
                    resolve_abbreviation_with_llm(word, text, possible_words)
                )
        else:
            expanded_words.append(word)
    return " ".join(expanded_words)


st.title("Transaction Categorizer with Local LLM")

# Upload files
categories_file = st.file_uploader(
    "Upload Categories File (Excel)", type=["xls", "xlsx"]
)
transactions_file = st.file_uploader(
    "Upload Transactions File (Excel)", type=["xls", "xlsx"]
)
# Define the abbreviation_dict path, adjust path if necessary
abbreviation_dict_path = "../data/abbreviation_dict.xlsx"

if categories_file and transactions_file:
    # Load data
    categories_df = pd.read_excel(categories_file)
    transactions_df = pd.read_excel(transactions_file)
    abbreviation_map = load_abbreviation_dict(abbreviation_dict_path)

    st.write("### Danh mục giao dịch")
    st.dataframe(categories_df)

    st.write("### Giao dịch")
    st.dataframe(transactions_df.head())

    # Lấy danh sách danh mục giao dịch
    category_list = categories_df.iloc[:, 0].tolist()  # Lấy cột đầu tiên làm danh mục
    category_list.append("Other")  # Thêm danh mục dự phòng

    # Mở rộng từ viết tắt trong nội dung giao dịch
    transactions_df["REMARK"] = transactions_df["REMARK"].apply(
        lambda x: expand_abbreviations(str(x), abbreviation_map)
    )

    # Tạo prompt bằng tiếng Việt
    transactions_text = "\n".join(transactions_df["REMARK"].astype(str).tolist())
    prompt = f"""
    Bạn là một AI có nhiệm vụ phân loại giao dịch tài chính vào các danh mục phù hợp.
    Danh mục có sẵn là: {', '.join(category_list)}.
    
    Hãy phân loại các giao dịch sau vào một trong các danh mục trên. Nếu không có danh mục nào phù hợp, hãy gán "Other".
    {transactions_text}
    
    Trả lời dưới dạng danh sách JSON gồm các từ điển chứa 'transaction' và 'category'.
    """

    # Chạy LLM để phân loại giao dịch
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    try:
        categorized_transactions = json.loads(response["message"]["content"])
        categorized_df = pd.DataFrame(categorized_transactions)

        # Đảm bảo tất cả các giao dịch có danh mục, nếu không, đặt thành "Other"
            prompt = f"""
    You are an AI that resolves abbreviations in financial transactions. Given the context:
    
    Transaction: "{context}"
    
    The abbreviation "{abbreviation}" could mean one of the following: {', '.join(possible_words)}.
    
    Which meaning is most appropriate? Reply with only the best matching word.
    """
        st.write("### Giao dịch đã được phân loại")
        st.dataframe(categorized_df)

        # Xuất tệp Excel
        output_file = "categorized_transactions.xlsx"
        categorized_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as file:
            st.download_button(
                "Tải xuống giao dịch đã phân loại",
                file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    except Exception as e:
        st.error(f"Không thể xử lý phản hồi từ LLM: {e}")
