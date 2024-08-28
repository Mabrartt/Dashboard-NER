import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import cm

def plot_top_entities(entity_counter, entity_type, top_n=10):
    sorted_entities = sorted(entity_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    if not sorted_entities:
        st.write(f"No {entity_type} entities to display.")
        return None
    
    unique_entities, counts = zip(*sorted_entities)
    colors = cm.get_cmap('tab10', top_n).colors
    fig, ax = plt.subplots()
    ax.barh(unique_entities, counts, color=colors)
    ax.set_xlabel('Counts')
    ax.set_title(f'Top {top_n} {entity_type} Entities')
    ax.invert_yaxis()
    return fig


def render_visualize():
    if 'pdf_data' in st.session_state:
        combined_seaweed = st.session_state['pdf_seaweed']
        combined_location = st.session_state['pdf_location']

        st.subheader("Total Entity Counts from PDF Data")
        pdf_total_seaweed = Counter(combined_seaweed)
        pdf_total_location = Counter(combined_location)
        pdf_count_df = pd.DataFrame({
            'Entity Type': ['SEAWEED', 'LOCATION'],
            'Unique Entities': [len(pdf_total_seaweed), len(pdf_total_location)],
            'Total Occurrences': [sum(pdf_total_seaweed.values()), sum(pdf_total_location.values())]
        })
        st.dataframe(pdf_count_df)

        st.subheader("Detailed Entity Counts from PDF Data")
        pdf_seaweed_df = pd.DataFrame(pdf_total_seaweed.items(), columns=['Entity', 'Count']).sort_values('Count', ascending=False).reset_index(drop=True)
        pdf_location_df = pd.DataFrame(pdf_total_location.items(), columns=['Entity', 'Count']).sort_values('Count', ascending=False).reset_index(drop=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("SEAWEED Entities")
            st.dataframe(pdf_seaweed_df)
        with col2:
            st.write("LOCATION Entities")
            st.dataframe(pdf_location_df)
        
        # Untuk download detail entity
        seaweed_csv = pdf_seaweed_df.to_csv(index=False)
        location_csv = pdf_location_df.to_csv(index=False)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Detailed Seaweed Entities",
                data=seaweed_csv,
                file_name="detailed_seaweed_entities.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                label="Download Detailed Location Entities",
                data=location_csv,
                file_name="detailed_location_entities.csv",
                mime="text/csv"
            )

        st.subheader("Top 10 SEAWEED Entities")
        pdf_seaweed_fig = plot_top_entities(pdf_total_seaweed, 'SEAWEED')
        if pdf_seaweed_fig:
            st.pyplot(pdf_seaweed_fig)

        st.subheader("Top 10 LOCATION Entities")
        pdf_location_fig = plot_top_entities(pdf_total_location, 'LOCATION')
        if pdf_location_fig:
            st.pyplot(pdf_location_fig)

    elif 'results_df' in st.session_state:
        results_df = st.session_state['results_df']
        total_seaweed = st.session_state['total_seaweed']
        total_location = st.session_state['total_location']

        st.subheader("Total Entity Counts")
        count_df = pd.DataFrame({
            'Entity Type': ['SEAWEED', 'LOCATION'],
            'Unique Entities': [len(total_seaweed), len(total_location)],
            'Total Occurrences': [sum(total_seaweed.values()), sum(total_location.values())]
        })
        st.dataframe(count_df)

        st.subheader("Detailed Entity Counts")
        seaweed_df = pd.DataFrame(total_seaweed.items(), columns=['Entity', 'Count']).sort_values('Count', ascending=False).reset_index(drop=True)
        location_df = pd.DataFrame(total_location.items(), columns=['Entity', 'Count']).sort_values('Count', ascending=False).reset_index(drop=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("SEAWEED Entities")
            st.dataframe(seaweed_df)
        with col2:
            st.write("LOCATION Entities")
            st.dataframe(location_df)
        
        # Untuk download detail entity
        seaweed_csv = seaweed_df.to_csv(index=False)
        location_csv = location_df.to_csv(index=False)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Detailed Seaweed Entities",
                data=seaweed_csv,
                file_name="detailed_seaweed_entities.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                label="Download Detailed Location Entities",
                data=location_csv,
                file_name="detailed_location_entities.csv",
                mime="text/csv"
            )

        st.subheader("Top 10 SEAWEED Entities")
        seaweed_fig = plot_top_entities(total_seaweed, 'SEAWEED')
        if seaweed_fig:
            st.pyplot(seaweed_fig)

        st.subheader("Top 10 LOCATION Entities")
        location_fig = plot_top_entities(total_location, 'LOCATION')
        if location_fig:
            st.pyplot(location_fig)

    else:
        st.write("Please go back to the Home page to perform NER predictions first.")

render_visualize()