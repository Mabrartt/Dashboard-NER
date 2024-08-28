import streamlit as st
import pandas as pd
import spacy
from collections import Counter
import fitz

def render_home():
    # Reset session state if file type changes
    if 'file_type' not in st.session_state:
        st.session_state['file_type'] = None

    file_type = st.radio("Select the type of file to upload:", ('Upload CSV/Excel', 'Upload PDF'), 
                         horizontal=True)

    if st.session_state['file_type'] != file_type:
        # Reset session state
        st.session_state.clear()
        st.session_state['file_type'] = file_type

    # Using spacy.load().
    import spacy
    nlp = spacy.load("en_pipeline")

    @st.cache_resource
    def load_model():
        return spacy.load("en_pipeline")

    def highlight_text(text):
        doc = nlp(text)
        seaweed_entities = Counter(ent.text.lower() for ent in doc.ents if ent.label_ == 'SEAWEED')
        location_entities = Counter(ent.text.lower() for ent in doc.ents if ent.label_ == 'LOCATION')

        highlighted_text = text
        colors = {"SEAWEED": "#FFA07A", "LOCATION": "#ADD8E6"}  
        for ent in doc.ents:
            label = ent.label_
            color = colors.get(label, "#FFFF00")  
            highlighted_text = highlighted_text.replace(ent.text, f'<span style="background-color:{color}">{ent.text}</span>')

        return seaweed_entities, location_entities, highlighted_text

    def format_entities(entities):
        if not entities:
            return ""
        return ', '.join([f"{ent} ({count})" for ent, count in entities.items()])

    st.markdown("""
        <style>
            th {
                text-align: center !important;
            }
        </style>
    """, unsafe_allow_html=True)

    def extract_pdf(file):
        doc = fitz.open(stream=file.read(), filetype='pdf')
        full_text = ""
        title = ""
        abstract = ""

        for i, page in enumerate(doc):
            text = page.get_text()
            full_text += text

            if i == 0:  
                lines = text.splitlines()
                if len(lines) > 0:
                    title = lines[0]  
                for j, line in enumerate(lines):
                    if "abstract" in line.lower():
                        abstract = " ".join(lines[j+1:j+5])  
                        break

        return title, abstract, full_text

    if file_type == 'Upload CSV/Excel':
        uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=['csv', 'xlsx'])

        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)

            if 'Abstract' in df.columns:
                st.write("Uploaded Dataset")
                st.dataframe(df[['Title', 'Abstract']])

                if st.button("Predict NER") or 'predicted' not in st.session_state:
                    results = []
                    total_seaweed = Counter()
                    total_location = Counter()

                    for i, row in enumerate(df.itertuples(), start=1):
                        title = getattr(row, 'Title', None)
                        abstract = row.Abstract
                        seaweed, location, highlighted_abstract = highlight_text(abstract)

                        result = {
                            'No.': i,
                            'Title': title,
                            'Abstract': highlighted_abstract,
                            'Seaweed Entities': format_entities(seaweed),
                            'Location Entities': format_entities(location)
                        }

                        results.append(result)
                        total_seaweed.update(seaweed)
                        total_location.update(location)

                    results_df = pd.DataFrame(results) 
                    st.session_state['results_df'] = results_df
                    st.session_state['total_seaweed'] = total_seaweed
                    st.session_state['total_location'] = total_location
                    st.session_state['predicted'] = True
                    
                results_df = st.session_state.get('results_df')

                rows_per_page = 10
                total_rows = len(results_df)
                total_pages = total_rows // rows_per_page + (1 if total_rows % rows_per_page > 0 else 0)

                if 'page' not in st.session_state:
                    st.session_state.page = 0

                start_row = st.session_state.page * rows_per_page
                end_row = min(start_row + rows_per_page, total_rows)

                results_df_page = results_df.iloc[start_row:end_row].copy()
                results_df_page.reset_index(drop=True, inplace=True)
                results_df_page['No.'] = range(start_row + 1, end_row + 1)

                st.write(results_df_page.to_html(escape=False, index=False), unsafe_allow_html=True)
                st.write(f"Page {st.session_state.page + 1} of {total_pages}")

                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("Previous Page"):
                        if st.session_state.page > 0:
                            st.session_state.page -= 1

                with col2:
                    if st.button("Next Page"):
                        if st.session_state.page < total_pages - 1:
                            st.session_state.page += 1

                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="abstracts_and_entities.csv",
                    mime="text/csv"
                )
            else:
                st.error("The uploaded file does not contain an 'Abstract' column.")

    elif file_type == 'Upload PDF':
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                title, abstract, full_text = extract_pdf(uploaded_file)
        
                seaweed_abstract, location_abstract, highlighted_abstract = highlight_text(abstract)
                seaweed_full_text, location_full_text, highlighted_full_text = highlight_text(full_text)
        
                st.session_state['pdf_seaweed'] = seaweed_full_text
                st.session_state['pdf_location'] = location_full_text
                st.session_state['pdf_data'] = True
                st.session_state['data_source'] = 'pdf'
            
                st.write("Title:", title)
                st.markdown(f"**Abstract:** {abstract}", unsafe_allow_html=True)

                with st.expander("See Full Text"):
                    st.markdown(full_text, unsafe_allow_html=True)
        
            seaweed_abstract, location_abstract, highlighted_abstract = highlight_text(abstract)
            seaweed_full_text, location_full_text, highlighted_full_text = highlight_text(full_text)

            st.write("NER Results")
            
            st.markdown(f"**Highlighted Abstract:** {highlighted_abstract}", unsafe_allow_html=True)

            with st.expander("See Highlighted Full Text"):
                st.markdown(highlighted_full_text, unsafe_allow_html=True)

            st.session_state['pdf_seaweed'] = seaweed_full_text
            st.session_state['pdf_location'] = location_full_text
            st.session_state['pdf_data'] = True

            df_csv = pd.DataFrame({
                'Title': [title],
                'Abstract': [abstract],
                'Full Text': [full_text],
                'Seaweed Entities': [format_entities(seaweed_abstract)],
                'Location Entities': [format_entities(location_abstract)],
            })
