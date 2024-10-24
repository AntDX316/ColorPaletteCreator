import streamlit as st
import pandas as pd
import base64
from io import StringIO
import colorsys

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

# Color mixing functions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(
        min(255, max(0, int(rgb[0]))),
        min(255, max(0, int(rgb[1]))),
        min(255, max(0, int(rgb[2])))
    )

def mix_colors(color1, color2, ratio=0.5):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    mixed_rgb = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))
    return rgb_to_hex(mixed_rgb)

def blend_colors(color1, color2, blend_mode="normal"):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    if blend_mode == "multiply":
        result = tuple(int((c1 * c2) / 255) for c1, c2 in zip(rgb1, rgb2))
    elif blend_mode == "screen":
        result = tuple(int(255 - ((255 - c1) * (255 - c2)) / 255) for c1, c2 in zip(rgb1, rgb2))
    elif blend_mode == "overlay":
        result = tuple(
            int(2 * c1 * c2 / 255) if c1 < 128 
            else int(255 - 2 * (255 - c1) * (255 - c2) / 255)
            for c1, c2 in zip(rgb1, rgb2)
        )
    else:  # normal blend
        result = tuple(int((c1 + c2) / 2) for c1, c2 in zip(rgb1, rgb2))
    
    return rgb_to_hex(result)

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
    
    # Main content tabs
    tab1, tab2 = st.tabs(["Color Palette", "Color Mixing"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("Color Mixing Studio")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            color1 = st.selectbox("Select first color", filtered_df['Name'], key='color1')
            color1_hex = filtered_df[filtered_df['Name'] == color1].iloc[0]['HEX']
            
            color2 = st.selectbox("Select second color", filtered_df['Name'], key='color2')
            color2_hex = filtered_df[filtered_df['Name'] == color2].iloc[0]['HEX']
            
            blend_mode = st.selectbox(
                "Select blend mode",
                ["normal", "multiply", "screen", "overlay"]
            )
            
            mix_ratio = st.slider("Mix ratio", 0.0, 1.0, 0.5, 0.1)
        
        with col2:
            st.subheader("Mixed Color Preview")
            
            # Display original colors
            st.markdown(
                f'<div style="display: flex; gap: 10px; margin-bottom: 20px;">'
                f'<div class="color-swatch" style="background-color: {color1_hex};"></div>'
                f'<div class="color-swatch" style="background-color: {color2_hex};"></div>'
                '</div>',
                unsafe_allow_html=True
            )
            
            # Display mixed color
            mixed_color = mix_colors(color1_hex, color2_hex, mix_ratio)
            blended_color = blend_colors(color1_hex, color2_hex, blend_mode)
            
            st.markdown("### Linear Mix")
            st.markdown(
                f'<div class="preview-box" style="background-color: {mixed_color};">'
                f'<p>HEX: {mixed_color}</p>'
                f'<p>Mix Ratio: {mix_ratio:.1f}</p>'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(f"### {blend_mode.title()} Blend")
            st.markdown(
                f'<div class="preview-box" style="background-color: {blended_color};">'
                f'<p>HEX: {blended_color}</p>'
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
