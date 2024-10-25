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
    r, g, b = [x/255 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_rgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return tuple(int(x * 255) for x in rgb)

# Color mixing functions
def mix_colors(color1_hex, color2_hex, ratio=0.5, blend_mode="normal"):
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    
    if blend_mode == "normal":
        mixed = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))
    elif blend_mode == "multiply":
        mixed = tuple(int((c1 * c2) / 255) for c1, c2 in zip(rgb1, rgb2))
    elif blend_mode == "screen":
        mixed = tuple(int(255 - ((255 - c1) * (255 - c2)) / 255) for c1, c2 in zip(rgb1, rgb2))
    else:  # overlay
        mixed = tuple(
            int(2 * c1 * c2 / 255) if c2 < 128 
            else int(255 - 2 * (255 - c1) * (255 - c2) / 255)
            for c1, c2 in zip(rgb1, rgb2)
        )
    
    return rgb_to_hex(mixed)

# Palette generation functions
def generate_monochromatic(base_color_hex, num_colors=5):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = []
    for i in range(num_colors):
        new_value = max(0.1, min(1.0, base_hsv[2] * (0.5 + i/(num_colors-1))))
        new_rgb = hsv_to_rgb((base_hsv[0], base_hsv[1], new_value))
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_complementary(base_color_hex):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    comp_hsv = ((base_hsv[0] + 0.5) % 1.0, base_hsv[1], base_hsv[2])
    comp_rgb = hsv_to_rgb(comp_hsv)
    return [base_color_hex, rgb_to_hex(comp_rgb)]

def generate_analogous(base_color_hex, num_colors=3):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = []
    angle = 0.1  # 36 degrees
    for i in range(num_colors):
        new_hue = (base_hsv[0] + (i - num_colors//2) * angle) % 1.0
        new_rgb = hsv_to_rgb((new_hue, base_hsv[1], base_hsv[2]))
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_triadic(base_color_hex):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = []
    for i in range(3):
        new_hue = (base_hsv[0] + i/3) % 1.0
        new_rgb = hsv_to_rgb((new_hue, base_hsv[1], base_hsv[2]))
        colors.append(rgb_to_hex(new_rgb))
    return colors

# Color harmony functions
def generate_split_complementary(base_color_hex):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = [base_color_hex]
    comp_hue = (base_hsv[0] + 0.5) % 1.0
    for offset in [-0.05, 0.05]:  # ±18 degrees
        new_hue = (comp_hue + offset) % 1.0
        new_rgb = hsv_to_rgb((new_hue, base_hsv[1], base_hsv[2]))
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_square_harmony(base_color_hex):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = [base_color_hex]
    for i in range(1, 4):
        new_hue = (base_hsv[0] + i/4) % 1.0
        new_rgb = hsv_to_rgb((new_hue, base_hsv[1], base_hsv[2]))
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_rectangular_harmony(base_color_hex):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsv = rgb_to_hsv(base_rgb)
    
    colors = [base_color_hex]
    offsets = [0.2, 0.5, 0.7]  # 72°, 180°, 252°
    for offset in offsets:
        new_hue = (base_hsv[0] + offset) % 1.0
        new_rgb = hsv_to_rgb((new_hue, base_hsv[1], base_hsv[2]))
        colors.append(rgb_to_hex(new_rgb))
    return colors

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

# Main function
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
    
    # Color Mixing Tab
    with tab2:
        st.subheader("Color Mixing")
        
        col1, col2 = st.columns(2)
        with col1:
            color1 = st.color_picker("Select first color", "#ff0000")
        with col2:
            color2 = st.color_picker("Select second color", "#0000ff")
        
        mix_ratio = st.slider("Mix ratio", 0.0, 1.0, 0.5, 0.01)
        blend_mode = st.selectbox("Blend mode", ["normal", "multiply", "screen", "overlay"])
        
        mixed_color = mix_colors(color1, color2, mix_ratio, blend_mode)
        
        st.markdown("### Mixed Color Preview")
        st.markdown(
            f'<div style="background-color: {mixed_color}; padding: 20px; border-radius: 10px; text-align: center; color: white;">'
            f'<p>Mixed Color: {mixed_color}</p>'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Palette Generator Tab
    with tab3:
        st.subheader("Palette Generator")
        
        base_color = st.color_picker("Choose base color", "#ff0000")
        palette_type = st.selectbox("Palette type", 
                                  ["Monochromatic", "Complementary", "Analogous", "Triadic"])
        
        if palette_type == "Monochromatic":
            num_colors = st.slider("Number of colors", 3, 7, 5)
            colors = generate_monochromatic(base_color, num_colors)
        elif palette_type == "Complementary":
            colors = generate_complementary(base_color)
        elif palette_type == "Analogous":
            num_colors = st.slider("Number of colors", 3, 5, 3)
            colors = generate_analogous(base_color, num_colors)
        else:  # Triadic
            colors = generate_triadic(base_color)
        
        st.markdown("### Generated Palette")
        cols = st.columns(len(colors))
        for idx, (color, col) in enumerate(zip(colors, cols)):
            with col:
                st.markdown(
                    f'<div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; color: white;">'
                    f'<p>{color}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
    
    # Color Harmony Tab
    with tab4:
        st.subheader("Color Harmony")
        
        base_color = st.color_picker("Choose base color", "#ff0000")
        harmony_type = st.selectbox("Harmony type", 
                                  ["Split Complementary", "Square", "Rectangular"])
        
        if harmony_type == "Split Complementary":
            colors = generate_split_complementary(base_color)
            description = "Split complementary colors are two colors adjacent to the complement of the base color."
        elif harmony_type == "Square":
            colors = generate_square_harmony(base_color)
            description = "Square harmony uses four colors evenly spaced around the color wheel."
        else:  # Rectangular
            colors = generate_rectangular_harmony(base_color)
            description = "Rectangular harmony uses two pairs of complementary colors."
        
        st.markdown("### Harmonious Colors")
        cols = st.columns(len(colors))
        for idx, (color, col) in enumerate(zip(colors, cols)):
            with col:
                st.markdown(
                    f'<div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; color: white;">'
                    f'<p>{color}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("### Description")
        st.markdown(description)
        
        st.markdown("### Usage Tips")
        st.markdown("""
        - Use harmonious colors to create visually pleasing designs
        - The base color should be your primary brand or theme color
        - Experiment with different harmony types to find the best match for your project
        - Consider using these colors for different elements like backgrounds, text, and accents
        """)
    
    # Color Finder Tab (existing implementation)
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
