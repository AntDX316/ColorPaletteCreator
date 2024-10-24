import streamlit as st
import pandas as pd
import base64
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Color Visualization Dashboard",
    page_icon="🎨",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('color_srgb.csv')
    return df

# Download function
def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'data:file/csv;base64,{b64}'
    return href

# Main function
def main():
    st.title("🎨 Color Visualization Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Search by name
    search_term = st.sidebar.text_input("Search by color name", "")
    
    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort by",
        ["Name", "HEX", "RGB"]
    )
    
    # Apply filters and sorting
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False)]
    
    if sort_by:
        filtered_df = filtered_df.sort_values(by=sort_by)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Color Palette")
        
        # Custom display of colors
        for _, row in filtered_df.iterrows():
            col_a, col_b, col_c = st.columns([1, 2, 2])
            with col_a:
                st.markdown(f'<div class="color-swatch" style="background-color: {row["HEX"]};"></div>',
                          unsafe_allow_html=True)
            with col_b:
                st.write(f"**{row['Name']}**")
                st.write(f"HEX: {row['HEX']}")
            with col_c:
                st.write("RGB: " + row['RGB'])
    
    with col2:
        st.subheader("Color Preview")
        if not filtered_df.empty:
            selected_color = st.selectbox("Select a color to preview", filtered_df['Name'])
            color_data = filtered_df[filtered_df['Name'] == selected_color].iloc[0]
            
            st.markdown(
                f'<div class="preview-box" style="background-color: {color_data["HEX"]};">'
                f'<h3>{color_data["Name"]}</h3>'
                f'<p>HEX: {color_data["HEX"]}</p>'
                f'<p>RGB: {color_data["RGB"]}</p>'
                '</div>',
                unsafe_allow_html=True
            )
    
    # Download section
    st.subheader("Download Data")
    download_link = get_download_link(filtered_df)
    st.markdown(
        f'<a href="{download_link}" download="filtered_colors.csv" '
        'class="download-button">Download Filtered Data as CSV</a>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
