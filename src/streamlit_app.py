import streamlit as st
import time
from parsers.place_parser import PlaceParser

# Page configuration
st.set_page_config(
    page_title="Lead Generation Tool",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False
if 'places_found' not in st.session_state:
    st.session_state.places_found = 0

# App header
st.title("🔍 Lead Generation Tool")
st.markdown("Search for businesses and automatically add qualified leads to Notion")

# Main content area
st.header("Search Queries")

# Input method selection
input_method = st.radio(
    "Choose input method:",
    ["Bulk Input (Multiple Queries)", "Single Query"],
    horizontal=True
)

if input_method == "Bulk Input (Multiple Queries)":
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
else:
    single_query = st.text_input(
        "Search Query",
        placeholder="e.g., restaurant in Philadelphia"
    )
    queries = [single_query] if single_query.strip() else []

# Search button
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    search_button = st.button(
        "🚀 Start Search & Export to Notion",
        type="primary",
        use_container_width=True,
        disabled=len(queries) == 0
    )

# Search execution
if search_button and queries:
    st.session_state.search_complete = False
    
    # Create parser instance
    parser = PlaceParser()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Results container
    results_container = st.container()
    
    with results_container:
        st.subheader("🔎 Search Progress")
        
        # Search each query
        for idx, query in enumerate(queries):
            progress = (idx + 1) / len(queries)
            progress_bar.progress(progress)
            status_text.text(f"Searching: {query} ({idx + 1}/{len(queries)})")
            
            # Create expander for this query
            with st.expander(f"Query {idx + 1}: {query}", expanded=True):
                search_start = time.time()
                
                # Perform search
                parser.search(query)
                
                search_time = time.time() - search_start
                
                # Display results
                new_places = len(parser.places)
                st.success(f"✅ Completed in {search_time:.2f}s")
                st.metric("Total Places Found", new_places)
        
        progress_bar.progress(1.0)
        status_text.text("✅ All searches completed!")
    
    # Summary
    st.divider()
    st.subheader("📊 Search Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Queries Processed", len(queries))
    with col2:
        st.metric("Places Found", len(parser.places))
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
                "Website": "✅" if place.website_uri else "❌"
            })
        
        st.dataframe(table_data, use_container_width=True)
        
        # Export section
        st.divider()
        st.subheader("💾 Exporting to Notion")
        
        with st.spinner("Exporting leads to Notion..."):
            try:
                parser.update_notion_with_places()
                st.success(f"✅ {len(parser.places)} leads exported to Notion successfully!")
            except Exception as e:
                st.error(f"❌ Error exporting to Notion: {str(e)}")
    else:
        st.warning("⚠️ No places found with email addresses.")
    
    st.session_state.search_complete = True
    st.session_state.places_found = len(parser.places)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <small>Lead Generation Tool | Powered by Google Places API & AI</small>
</div>
""", unsafe_allow_html=True)