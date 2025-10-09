import streamlit as st

import subprocess
import time

from parsers.place_parser import PlaceParser
from tools.keys import get_secret

APP_PASSWORD = get_secret("APP_PASSWORD")

# Install Playwright browsers (only first startup)
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print("Playwright setup skipped:", e)

def check_password():
    """Return True if the user entered the correct password."""
    if "password_correct" not in st.session_state:
        st.text_input("Enter password:", type="password", key="password_input")
        if st.session_state.password_input == APP_PASSWORD:
            st.session_state.password_correct = True
            del st.session_state.password_input
        else:
            st.error("Incorrect password")
            return False
    return st.session_state.password_correct

# Page configuration
st.set_page_config(
    page_title="Lead Generation Tool",
    page_icon="🔍",
    layout="wide"
)

if check_password():
    # Initialize session state
    if 'search_complete' not in st.session_state:
        st.session_state.search_complete = False
    if 'places_found' not in st.session_state:
        st.session_state.places_found = 0
    if 'searching' not in st.session_state:
        st.session_state.searching = False
    if 'parser' not in st.session_state:
        st.session_state.parser = None

    # Only show input and button if not currently searching
    if not st.session_state.searching:
        # Main content area
        st.header("Search Leads")

        st.markdown("Enter one search query per line:")
        queries_text = st.text_area(
            "Search Queries",
            height=200,
            placeholder="restaurant in Philadelphia\ncoffee shop in New York\nbar in Boston\nrestaurant in Miami",
            label_visibility="collapsed"
        )
        
        # Parse queries
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
        
        if queries:
            st.info(f"📋 {len(queries)} queries ready to search")
            with st.expander("Preview queries"):
                for i, q in enumerate(queries, 1):
                    st.write(f"{i}. {q}")

        # Search button
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            search_button = st.button(
                "🚀 Start Search & Export to Notion",
                type="primary",
                width="stretch",
                disabled=len(queries) == 0
            )

        # Set searching state when button is clicked
        if search_button and queries:
            st.session_state.searching = True
            st.session_state.queries = queries
            st.rerun()

    # Search execution (only visible when searching)
    if st.session_state.searching:
        queries = st.session_state.queries
        st.session_state.search_complete = False
        
        # Create parser instance
        parser = PlaceParser()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Container for query results
        results_container = st.container()

        with results_container:
            st.subheader("🔎 Search Progress")

            total_queries = len(queries)
            total_leads_found = 0
            total_exported = 0

            # Create placeholders for live updates
            export_status = st.empty()
            leads_table = st.empty()

            for idx, query in enumerate(queries):
                progress_bar.progress((idx / total_queries) * 0.5)  # First half for searching
                status_text.text(f"Searching query {idx + 1}/{total_queries}: {query}")

                with st.expander(f"Query {idx + 1}: {query}", expanded=True):
                    query_results_placeholder = st.empty()
                    
                    with st.spinner(f"🔄 Fetching places for: {query}..."):
                        search_start = time.time()

                        # Perform search and export places as they're found
                        initial_count = len(parser.places)
                        parser.search_and_export(query, export_status, leads_table)
                        
                        search_time = time.time() - search_start
                    
                    new_places = len(parser.places) - total_leads_found
                    total_leads_found = len(parser.places)
                    total_exported = total_leads_found  # All found places are exported immediately

                    query_results_placeholder.success(f"✅ Query completed in {search_time:.2f}s")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Leads Found This Query", new_places)
                    with col2:
                        st.metric("Exported This Query", new_places)

            # Final updates after all queries
            progress_bar.progress(1.0)
            status_text.success("✅ All queries completed and exported!")

        # Summary
        st.divider()
        st.subheader("📊 Search Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Queries Processed", len(queries))
        with col2:
            st.metric("Places Found & Exported", len(parser.places))
        with col3:
            avg_score = sum(p.lead_score for p in parser.places.values()) / len(parser.places) if parser.places else 0
            st.metric("Avg Lead Score", f"{avg_score:.2f}")
        
        # Display found places
        if parser.places:
            st.subheader("🎯 Leads Found")
            
            # Create a table view
            table_data = []
            for place in parser.places.values():
                table_data.append({
                    "Business": place.display_name,
                    "Lead Score": f"{place.lead_score}/5.00",
                    "Rating": f"{place.rating} ⭐" if place.rating else "N/A",
                    "Phone": place.national_phone_number or "N/A",
                    "Emails": ", ".join(place.emails[:2]) if place.emails else "N/A",
                    "Website": "✅" if place.website_uri else "❌",
                    "Status": "✅ Exported"
                })
            
            st.dataframe(table_data, width="stretch")
        else:
            st.warning("⚠️ No places found with email addresses.")
        
        st.session_state.search_complete = True
        st.session_state.places_found = len(parser.places)
        st.session_state.searching = False
        st.session_state.parser = parser
        
        # Add button to start new search
        st.divider()
        if st.button("🔄 Start New Search", type="primary"):
            st.session_state.searching = False
            st.session_state.search_complete = False
            st.rerun()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <small>Lead Generation Tool | Powered by Google Places API & AI</small>
    </div>
    """, unsafe_allow_html=True)