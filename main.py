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

def rgb_to_hsv(rgb):
    r, g, b = [x/255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_rgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return tuple(int(x * 255) for x in rgb)

def blend_colors(color1_hex, color2_hex, ratio=0.5, mode="normal"):
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    
    if mode == "normal":
        blended = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))
    elif mode == "multiply":
        blended = tuple(int((c1 * c2) / 255) for c1, c2 in zip(rgb1, rgb2))
    elif mode == "screen":
        blended = tuple(int(255 - ((255 - c1) * (255 - c2)) / 255) for c1, c2 in zip(rgb1, rgb2))
    elif mode == "overlay":
        blended = tuple(
            int(2 * c1 * c2 / 255) if c2 < 128 
            else int(255 - 2 * (255 - c1) * (255 - c2) / 255)
            for c1, c2 in zip(rgb1, rgb2)
        )
    
    return rgb_to_hex(blended)

def generate_palette(base_color_hex, scheme_type):
    base_rgb = hex_to_rgb(base_color_hex)
    h, s, v = rgb_to_hsv(base_rgb)
    
    if scheme_type == "monochromatic":
        colors = [
            hsv_to_rgb((h, max(0.2, s - 0.3), min(1.0, v + 0.3))),
            hsv_to_rgb((h, s, v)),
            hsv_to_rgb((h, min(1.0, s + 0.3), max(0.2, v - 0.3)))
        ]
    elif scheme_type == "complementary":
        colors = [
            base_rgb,
            hsv_to_rgb(((h + 0.5) % 1.0, s, v))
        ]
    elif scheme_type == "analogous":
        colors = [
            hsv_to_rgb(((h - 0.083) % 1.0, s, v)),
            base_rgb,
            hsv_to_rgb(((h + 0.083) % 1.0, s, v))
        ]
    elif scheme_type == "triadic":
        colors = [
            base_rgb,
            hsv_to_rgb(((h + 0.333) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.666) % 1.0, s, v))
        ]
    else:
        colors = [base_rgb]
        
    return [rgb_to_hex(rgb) for rgb in colors]

def get_harmony_colors(base_color_hex, harmony_type):
    base_rgb = hex_to_rgb(base_color_hex)
    h, s, v = rgb_to_hsv(base_rgb)
    
    if harmony_type == "split-complementary":
        colors = [
            base_rgb,
            hsv_to_rgb(((h + 0.5 - 0.083) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.5 + 0.083) % 1.0, s, v))
        ]
    elif harmony_type == "square":
        colors = [
            base_rgb,
            hsv_to_rgb(((h + 0.25) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.5) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.75) % 1.0, s, v))
        ]
    elif harmony_type == "rectangular":
        colors = [
            base_rgb,
            hsv_to_rgb(((h + 0.167) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.5) % 1.0, s, v)),
            hsv_to_rgb(((h + 0.667) % 1.0, s, v))
        ]
    else:
        colors = [base_rgb]
    
    return [rgb_to_hex(rgb) for rgb in colors]

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
    
    distances.sort(key=lambda x: x[0])
    return [row for _, row in distances[:num_colors]]

def main():
    st.title("🎨 Color Visualization Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    search_term = st.sidebar.text_input("Search by color name", "")
    sort_by = st.sidebar.selectbox("Sort by", ["Name", "HEX", "RGB"])
    
    # Apply filters and sorting
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False)]
    if sort_by:
        filtered_df = filtered_df.sort_values(by=sort_by)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Color Palette", "Color Mixing", "Palette Generator", "Color Harmony", "Color Finder"])
    
    # Color Palette Tab
    with tab1:
        st.subheader("Color Palette")
        
        # Display colors in a grid
        cols = st.columns(4)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 4]:
                st.markdown(
                    f'<div class="preview-box" style="background-color: {row["HEX"]};">'
                    f'<p>{row["Name"]}</p>'
                    f'<p>HEX: {row["HEX"]}</p>'
                    f'<p>RGB: {row["RGB"]}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
    
    # Color Mixing Tab
    with tab2:
        st.subheader("Color Mixing")
        
        col1, col2 = st.columns(2)
        with col1:
            color1 = st.color_picker("Select first color", "#ff0000", key="mix_color1")
            color2 = st.color_picker("Select second color", "#0000ff", key="mix_color2")
        
        with col2:
            blend_mode = st.selectbox("Blend Mode", ["normal", "multiply", "screen", "overlay"])
            mix_ratio = st.slider("Mix Ratio", 0.0, 1.0, 0.5)
        
        result_color = blend_colors(color1, color2, mix_ratio, blend_mode)
        
        st.markdown("### Result")
        st.markdown(
            f'<div style="display: flex; gap: 10px; margin: 20px 0;">'
            f'<div class="preview-box" style="flex: 1; background-color: {color1};"><p>Color 1</p></div>'
            f'<div class="preview-box" style="flex: 1; background-color: {result_color};"><p>Blended</p></div>'
            f'<div class="preview-box" style="flex: 1; background-color: {color2};"><p>Color 2</p></div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Palette Generator Tab
    with tab3:
        st.subheader("Palette Generator")
        
        base_color = st.color_picker("Select base color", "#ff0000", key="palette_base_color")
        scheme_type = st.selectbox(
            "Select color scheme",
            ["monochromatic", "complementary", "analogous", "triadic"]
        )
        
        palette = generate_palette(base_color, scheme_type)
        
        st.markdown("### Generated Palette")
        cols = st.columns(len(palette))
        for color, col in zip(palette, cols):
            with col:
                st.markdown(
                    f'<div class="preview-box" style="background-color: {color};">'
                    f'<p>HEX: {color}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
    
    # Color Harmony Tab
    with tab4:
        st.subheader("Color Harmony")
        
        base_color = st.color_picker("Select base color", "#ff0000", key="harmony_base_color")
        harmony_type = st.selectbox(
            "Select harmony type",
            ["split-complementary", "square", "rectangular"]
        )
        
        harmony_colors = get_harmony_colors(base_color, harmony_type)
        
        st.markdown("### Harmony Colors")
        cols = st.columns(len(harmony_colors))
        for color, col in zip(harmony_colors, cols):
            with col:
                st.markdown(
                    f'<div class="preview-box" style="background-color: {color};">'
                    f'<p>HEX: {color}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("### Usage Tips")
        harmony_tips = {
            "split-complementary": "Use the base color as dominant, and the split colors as accents.",
            "square": "Create balanced designs with equal visual weight for each color.",
            "rectangular": "Use for sophisticated designs with two pairs of complementary colors."
        }
        st.info(harmony_tips[harmony_type])
    
    # Color Finder Tab
    with tab5:
        st.subheader("Color Finder")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Pick a Color")
            picked_color = st.color_picker("Choose a color", "#000000", key="finder_color")
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
