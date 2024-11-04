import streamlit as st
import sqlite3
import pandas as pd

# Funkcja do wyszukiwania danych w bazie SQLite
def search_by_criteria(year_range, keywords):
    conn = sqlite3.connect('PLAN_B.db')  # Połącz z bazą danych SQLite
    min_year, max_year = year_range
    LP = 0
    NP = 0
    if keywords == "light pollution":
        LP = 1
    elif keywords == "noise pollution":
        NP = 1
    else:
        LP = 1
        NP = 1
    query = """
    SELECT id, title, author, year, abstract, doi, entry_type, keywords 
    FROM Bibliografia 
    WHERE year BETWEEN ? AND ? 
    AND lightPollution = ? AND noisePollution = ?
    """
    keyword_filter = f"%{keywords}%"
    df = pd.read_sql_query(query, conn, params=(min_year, max_year, LP, NP))
    conn.close()
    return df

# Interfejs aplikacji
st.title("Search publications by year and keywords")

# Suwaki do wyboru zakresu lat
year_range = st.slider(
    "Select a range of publication years:",
    min_value=1900,
    max_value=2024,
    value=(2000, 2024),
    step=1,
)

# Pole wyboru dla słów kluczowych
keyword_options = ["light pollution", "noise pollution", "light and noise pollution"]
selected_keyword = st.selectbox("Select a keyword to filter by:", keyword_options)

# Przycisk do uruchomienia wyszukiwania
if st.button("Search"):
    # Pobieranie wyników z bazy danych
    results = search_by_criteria(year_range, selected_keyword)
    
    # Wyświetlanie liczby wyselekcjonowanych rekordów
    st.write(f"Number of publications found: {len(results)}")
    
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
