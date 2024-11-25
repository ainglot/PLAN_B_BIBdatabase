import streamlit as st
import sqlite3
import pandas as pd

# Funkcja do wyszukiwania danych w bazie SQLite
def search_by_criteria(year_range, research_problem, keywords):
    conn = sqlite3.connect('PLAN_B.db')  # Połącz z bazą danych SQLite
    min_year, max_year = year_range

    # Przetwarzanie wpisanych słów kluczowych
    if keywords:
        keyword_list = [kw.strip() for kw in keywords.split(";") if kw.strip()]
        keyword_placeholders = " OR ".join(["keywords LIKE ?"] * len(keyword_list))
        keyword_params = [f"%{kw}%" for kw in keyword_list]
    else:
        keyword_placeholders = None
        keyword_params = []

    # Tworzenie zapytania SQL z opcjonalnym filtrem dla research_problem
    if research_problem == "ALL":
        query = """
        SELECT id, title, author, year, abstract, doi, entry_type, keywords 
        FROM Bibliografia 
        WHERE year BETWEEN ? AND ?
        """
        params = (min_year, max_year)
    else:
        query = """
        SELECT id, title, author, year, abstract, doi, entry_type, keywords 
        FROM Bibliografia 
        WHERE year BETWEEN ? AND ? 
        AND research_problem = ?
        """
        params = (min_year, max_year, research_problem)
    
    # Dodanie filtru słów kluczowych (jeśli wpisano słowa kluczowe)
    if keyword_placeholders:
        query += f" AND ({keyword_placeholders})"
        params.extend(keyword_params)
    
    # Wykonanie zapytania SQL
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Interfejs aplikacji
st.title("Search publications by year, keywords, and research problem")

# Suwaki do wyboru zakresu lat
year_range = st.slider(
    "Select a range of publication years:",
    min_value=1970,
    max_value=2024,
    value=(2010, 2024),
    step=1,
)

# Pole wyboru dla słów kluczowych
keyword_options = ["ALL", "LPMeasures", "LPMitigation", "NPMeasures", "NPMitigation"]
selected_keyword = st.selectbox("Select a keyword to filter by:", keyword_options)

# Pole tekstowe do wprowadzania słów kluczowych
user_input_keywords = st.text_input("Enter keywords separated by semicolons (e.g., Animals; Birds; Cities):")

# Przycisk do uruchomienia wyszukiwania
if st.button("Search"):
    # Wywołanie funkcji wyszukiwania
    results = search_by_criteria(year_range, selected_keyword, user_input_keywords)
    
    # Wyświetlanie liczby wyselekcjonowanych rekordów
    st.write(f"**Number of publications found: {len(results)}**")
    
    # Nowe okno
    with st.expander("Search Results", expanded=True):
        if not results.empty:
            # Wyświetlanie wyników
            for index, row in results.iterrows():
                st.write(f"### Publication {index + 1}")
                st.write(f"**ID:** {row['id']}")
                st.write(f"**Authors:** {row['author']}")
                st.write(f"**Title:** {row['title']}")
                st.write(f"**Keywords:** {row['keywords']}")
                st.write(f"**Year:** {row['year']}")
                st.write(f"**Abstract:** {row['abstract']}")
                if row['doi']:
                    doi_link = f"[{row['doi']}](https://doi.org/{row['doi']})"
                else:
                    doi_link = "Brak"
                st.write(f"**DOI:** {doi_link}")
                st.write("---")  # Dodaje linię oddzielającą wyniki
        else:
            st.write("No results for the specified criteria.")
