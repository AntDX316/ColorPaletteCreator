import streamlit as st
import pandas as pd
import base64
from io import StringIO
import colorsys
import math

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

# New Color Harmony Functions
def get_split_complementary(base_color, angle=30):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Calculate split complementary colors
    angle_percent = angle / 360.0
    complement_h = (h + 0.5) % 1.0
    h1 = (complement_h - angle_percent) % 1.0
    h2 = (complement_h + angle_percent) % 1.0
    
    rgb1 = hsv_to_rgb((h1, s, v))
    rgb2 = hsv_to_rgb((h2, s, v))
    
    return [base_color, rgb_to_hex(rgb1), rgb_to_hex(rgb2)]

def get_square_harmony(base_color):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Calculate colors at 90° intervals
    colors = []
    for i in range(4):
        new_h = (h + (i * 0.25)) % 1.0
        rgb = hsv_to_rgb((new_h, s, v))
        colors.append(rgb_to_hex(rgb))
    
    return colors

def get_rectangular_harmony(base_color):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Calculate colors for rectangular harmony (60° and 120° apart)
    h1 = (h + 0.167) % 1.0  # 60°
    h2 = (h + 0.5) % 1.0    # 180°
    h3 = (h + 0.667) % 1.0  # 240°
    
    colors = [
        base_color,
        rgb_to_hex(hsv_to_rgb((h1, s, v))),
        rgb_to_hex(hsv_to_rgb((h2, s, v))),
        rgb_to_hex(hsv_to_rgb((h3, s, v)))
    ]
    
    return colors

# Existing functions remain the same
def generate_monochromatic(base_color, count=5):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    colors = []
    step = 1.0 / (count - 1)
    
    for i in range(count):
        new_v = max(0.1, min(1.0, 0.1 + i * step))
        rgb = hsv_to_rgb((h, s, new_v))
        colors.append(rgb_to_hex(rgb))
    
    return colors

def generate_complementary(base_color):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Generate complementary color (opposite on color wheel)
    comp_h = (h + 0.5) % 1.0
    comp_rgb = hsv_to_rgb((comp_h, s, v))
    
    return [base_color, rgb_to_hex(comp_rgb)]

def generate_analogous(base_color, angle=30):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Convert angle to percentage of color wheel
    angle_percent = angle / 360.0
    
    # Generate colors on both sides
    h1 = (h - angle_percent) % 1.0
    h2 = (h + angle_percent) % 1.0
    
    rgb1 = hsv_to_rgb((h1, s, v))
    rgb2 = hsv_to_rgb((h2, s, v))
    
    return [rgb_to_hex(rgb1), base_color, rgb_to_hex(rgb2)]

def generate_triadic(base_color):
    base_rgb = hex_to_rgb(base_color)
    h, s, v = rgb_to_hsv(base_rgb)
    
    # Generate two colors at 120° intervals
    h1 = (h + 1/3) % 1.0
    h2 = (h + 2/3) % 1.0
    
    rgb1 = hsv_to_rgb((h1, s, v))
    rgb2 = hsv_to_rgb((h2, s, v))
    
    return [base_color, rgb_to_hex(rgb1), rgb_to_hex(rgb2)]

# Color mixing functions
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
    tab1, tab2, tab3, tab4 = st.tabs(["Color Palette", "Color Mixing", "Palette Generator", "Color Harmony"])
    
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

    with tab3:
        st.subheader("Palette Generator")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            base_color = st.selectbox("Select base color", filtered_df['Name'], key='base_color')
            base_color_hex = filtered_df[filtered_df['Name'] == base_color].iloc[0]['HEX']
            
            palette_type = st.selectbox(
                "Select palette type",
                ["Monochromatic", "Complementary", "Analogous", "Triadic"]
            )
            
            if palette_type == "Monochromatic":
                count = st.slider("Number of colors", 3, 7, 5)
                colors = generate_monochromatic(base_color_hex, count)
            elif palette_type == "Complementary":
                colors = generate_complementary(base_color_hex)
            elif palette_type == "Analogous":
                angle = st.slider("Angle", 10, 50, 30)
                colors = generate_analogous(base_color_hex, angle)
            else:  # Triadic
                colors = generate_triadic(base_color_hex)
        
        with col2:
            st.subheader("Generated Palette")
            
            # Display all colors in the palette
            cols = st.columns(len(colors))
            for idx, (color, col) in enumerate(zip(colors, cols)):
                with col:
                    st.markdown(
                        f'<div class="preview-box" style="background-color: {color};">'
                        f'<p>Color {idx + 1}</p>'
                        f'<p>HEX: {color}</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
    
    with tab4:
        st.subheader("Color Harmony Suggestions")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            harmony_base_color = st.selectbox("Select base color", filtered_df['Name'], key='harmony_base_color')
            harmony_base_hex = filtered_df[filtered_df['Name'] == harmony_base_color].iloc[0]['HEX']
            
            harmony_type = st.selectbox(
                "Select harmony type",
                ["Split Complementary", "Square", "Rectangle"]
            )
            
            if harmony_type == "Split Complementary":
                split_angle = st.slider("Split angle", 10, 45, 30)
                harmony_colors = get_split_complementary(harmony_base_hex, split_angle)
                harmony_description = """
                Split complementary colors consist of a base color and two colors adjacent to its complement.
                This creates high contrast while being more sophisticated than a standard complementary scheme.
                """
            elif harmony_type == "Square":
                harmony_colors = get_square_harmony(harmony_base_hex)
                harmony_description = """
                Square harmony uses four colors evenly spaced around the color wheel (90° apart).
                This creates a bold and balanced color scheme with maximum contrast.
                """
            else:  # Rectangle
                harmony_colors = get_rectangular_harmony(harmony_base_hex)
                harmony_description = """
                Rectangular harmony uses four colors arranged in two complementary pairs.
                This creates a rich color scheme with plenty of possibilities for variation.
                """
        
        with col2:
            st.markdown("### Harmony Preview")
            st.markdown(harmony_description)
            
            # Display harmony colors
            cols = st.columns(len(harmony_colors))
            for idx, (color, col) in enumerate(zip(harmony_colors, cols)):
                with col:
                    st.markdown(
                        f'<div class="preview-box" style="background-color: {color};">'
                        f'<p>Color {idx + 1}</p>'
                        f'<p>HEX: {color}</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            
            # Color harmony tips
            st.markdown("### Usage Tips")
            st.markdown("""
            - Use the base color as your primary color
            - Use harmony colors for accents and highlights
            - Maintain a consistent ratio between colors (e.g., 60-30-10 rule)
            - Consider the context and purpose of your design
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
