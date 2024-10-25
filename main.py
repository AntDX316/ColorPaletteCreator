import streamlit as st
import pandas as pd
import base64
from io import StringIO
import colorsys
import math

# Load data function
@st.cache_data
def load_data():
    df = pd.read_csv('color_srgb.csv')
    return df

# Color conversion functions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(
        min(255, max(0, int(rgb[0]))),
        min(255, max(0, int(rgb[1]))),
        min(255, max(0, int(rgb[2])))
    )

# Download function
def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'data:file/csv;base64,{b64}'
    return href

def calculate_color_distance(color1_hex, color2_hex):
    """Calculate Euclidean distance between two colors in RGB space"""
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

def find_similar_colors(target_color, df, num_colors=5):
    """Find similar colors in the dataset"""
    distances = []
    for _, row in df.iterrows():
        distance = calculate_color_distance(target_color, row['HEX'])
        distances.append((distance, row))
    
    # Sort by distance and get top matches
    distances.sort(key=lambda x: x[0])
    return [row for _, row in distances[:num_colors]]

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
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Color Palette", "Color Mixing", "Palette Generator", "Color Harmony", "Color Finder"])
    
    with tab5:
        st.subheader("Color Finder")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Pick a Color")
            picked_color = st.color_picker("Choose a color", "#000000")
            num_similar = st.slider("Number of similar colors", 3, 10, 5)
            
            st.markdown("### Selected Color")
            st.markdown(
                f'<div class="preview-box" style="background-color: {picked_color};">'
                f'<p>HEX: {picked_color}</p>'
                '</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown("### Similar Colors")
            similar_colors = find_similar_colors(picked_color, df, num_similar)
            
            # Display similar colors in a grid
            cols = st.columns(min(3, len(similar_colors)))
            for idx, (color, col) in enumerate(zip(similar_colors, cols * (len(similar_colors) // 3 + 1))):
                if idx < len(similar_colors):
                    with col:
                        st.markdown(
                            f'<div class="preview-box" style="background-color: {color["HEX"]};">'
                            f'<p>{color["Name"]}</p>'
                            f'<p>HEX: {color["HEX"]}</p>'
                            f'<p>RGB: {color["RGB"]}</p>'
                            '</div>',
                            unsafe_allow_html=True
                        )
            
            st.markdown("### How it works")
            st.markdown("""
            The color finder tool uses RGB color space to calculate the Euclidean distance between colors.
            The smaller the distance, the more similar the colors are. The tool returns the closest matching
            colors from our dataset based on this calculation.
            
            Tips for using the color finder:
            - Use the color picker to select any color
            - Adjust the number of similar colors to see more or fewer matches
            - Colors are matched based on their RGB values
            """)
    
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
