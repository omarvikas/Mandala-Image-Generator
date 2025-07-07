import streamlit as st
import openai
import requests
from PIL import Image
import io
import base64
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Mandala Art Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4A90E2;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .inspiration-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: white;
    }
    .download-btn {
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_openai(api_key):
    """Initialize OpenAI client with API key"""
    if api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            return client
        except Exception as e:
            st.error(f"❌ Invalid API Key: {str(e)}")
            return None
    return None

def create_mandala_prompt(user_inspiration, style_preference, color_scheme, num_axes):
    """Create a detailed prompt for DALL-E 3 mandala generation"""
    base_prompt = f"""Create a beautiful, intricate mandala art inspired by: {user_inspiration}. 
    
    The mandala should be:
    - Perfectly symmetrical and circular with {num_axes}-fold rotational symmetry
    - {num_axes} identical sections radiating from the center
    - Highly detailed with intricate patterns repeating every {360//num_axes} degrees
    - {style_preference} style
    - Using {color_scheme} color palette
    - Centered on a clean background
    - Sacred geometry elements with {num_axes}-way symmetry
    - Meditative and harmonious design
    - Professional digital art quality
    
    Style: Detailed mandala artwork, spiritual, geometric, ornate patterns, {num_axes}-fold symmetry"""
    
    return base_prompt

def generate_mandala(client, prompt):
    """Generate mandala using DALL-E 3"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def download_image(image_url):
    """Download image from URL and return as bytes"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return response.content
        else:
            st.error("Failed to download image")
            return None
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def create_download_link(image_bytes, filename):
    """Create a download link for the image"""
    b64 = base64.b64encode(image_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}" class="download-btn">📥 Download Mandala</a>'
    return href

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 Mandala Art Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your inspiration into beautiful mandala art using AI</p>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    # Sidebar for settings
    st.sidebar.title("🎨 Mandala Settings")
    
    # Number of axes for symmetry
    num_axes = st.sidebar.slider(
        "Number of Symmetry Axes:",
        min_value=3,
        max_value=12,
        value=8,
        step=1,
        help="Controls the rotational symmetry of the mandala (e.g., 4 = 4-fold symmetry, 8 = 8-fold symmetry)"
    )
    
    # Display symmetry info
    st.sidebar.info(f"🔄 Your mandala will have {num_axes}-fold rotational symmetry with {num_axes} identical sections")
    
    # Style preferences
    style_options = [
        "Traditional Buddhist",
        "Modern geometric",
        "Floral and organic",
        "Celtic inspired",
        "Tibetan style",
        "Art Nouveau",
        "Minimalist",
        "Psychedelic"
    ]
    
    color_options = [
        "Vibrant rainbow",
        "Earth tones",
        "Monochromatic blue",
        "Golden and amber",
        "Purple and violet",
        "Black and white",
        "Pastel colors",
        "Jewel tones"
    ]
    
    style_preference = st.sidebar.selectbox("Choose Style:", style_options)
    color_scheme = st.sidebar.selectbox("Choose Color Scheme:", color_options)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="inspiration-box">', unsafe_allow_html=True)
        st.markdown("### 🔑 API Key & Inspiration")
        
        # API Key input
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/"
        )
        
        # User input
        user_inspiration = st.text_area(
            "What inspires your mandala? (e.g., nature, emotions, experiences, dreams)",
            placeholder="Enter your inspiration here... (e.g., 'sunset over mountains', 'feeling of peace and harmony', 'blooming lotus flower')",
            height=100
        )
        
        # Example inspirations
        st.markdown("#### 💡 Need inspiration? Try these:")
        example_inspirations = [
            "Ocean waves and seashells",
            "Mountain peaks and pine trees",
            "Butterfly wings and flowers",
            "Stars and cosmic energy",
            "Ancient wisdom and meditation",
            "Fire and transformation",
            "Seasons changing",
            "Inner peace and balance"
        ]
        
        selected_example = st.selectbox("Or choose an example:", [""] + example_inspirations)
        if selected_example:
            user_inspiration = selected_example
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate button
        # Generate button
        if st.button("🎨 Generate Mandala", type="primary", use_container_width=True):
            if not api_key.strip():
                st.error("❌ Please enter your OpenAI API Key")
                st.info("""
                ### How to get your OpenAI API Key:
                1. Go to [OpenAI Platform](https://platform.openai.com/)
                2. Sign up or log in to your account
                3. Navigate to API Keys section
                4. Create a new API key
                5. Copy and paste it above
                """)
            elif not user_inspiration.strip():
                st.warning("Please enter your inspiration to generate a mandala!")
            else:
                # Initialize OpenAI client
                client = initialize_openai(api_key)
                
                if client:
                    with st.spinner("Creating your mandala... This may take a few moments"):
                        prompt = create_mandala_prompt(user_inspiration, style_preference, color_scheme, num_axes)
                        
                        # Store the prompt for display
                        st.session_state.current_prompt = prompt
                        
                        # Generate the mandala
                        image_url = generate_mandala(client, prompt)
                        
                        if image_url:
                            st.session_state.current_image_url = image_url
                            st.session_state.current_inspiration = user_inspiration
                            st.session_state.current_num_axes = num_axes
                            st.success("✨ Your mandala has been created!")
                            st.rerun()
    
    with col2:
        st.markdown("### 🖼️ Your Generated Mandala")
        
        # Display generated image
        if hasattr(st.session_state, 'current_image_url'):
            try:
                # Download and display image
                image_bytes = download_image(st.session_state.current_image_url)
                if image_bytes:
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=f"Inspired by: {st.session_state.current_inspiration}", use_container_width=True)
                    
                    # Download button
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"mandala_{timestamp}.png"
                    download_link = create_download_link(image_bytes, filename)
                    st.markdown(download_link, unsafe_allow_html=True)
                    
                    # Display generation details
                    with st.expander("🔍 Generation Details"):
                        st.write(f"**Inspiration:** {st.session_state.current_inspiration}")
                        st.write(f"**Style:** {style_preference}")
                        st.write(f"**Color Scheme:** {color_scheme}")
                        if hasattr(st.session_state, 'current_num_axes'):
                            st.write(f"**Symmetry Axes:** {st.session_state.current_num_axes}-fold symmetry")
                        st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        if hasattr(st.session_state, 'current_prompt'):
                            st.write("**Full Prompt:**")
                            st.code(st.session_state.current_prompt, language="text")
                
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")
        else:
            st.info("👈 Enter your OpenAI API Key and inspiration, then click 'Generate Mandala' to create your art!")
            
            # Display example mandala description
            st.markdown("""
            **Your mandala will be:**
            - Perfectly symmetrical and circular
            - Customizable symmetry axes (3-12 fold)
            - Highly detailed with intricate patterns
            - Customized to your inspiration
            - Available in high resolution (1024x1024)
            - Ready for download as PNG
            
            **Symmetry Examples:**
            - 4 axes = Cross-like pattern
            - 6 axes = Hexagonal pattern
            - 8 axes = Traditional mandala
            - 12 axes = Highly detailed pattern
            
            **Need an OpenAI API Key?**
            - Visit [OpenAI Platform](https://platform.openai.com/)
            - Sign up and navigate to API Keys
            - Create a new key and paste it above
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🧘 Made with love using Streamlit and OpenAI DALL-E 3</p>
        <p>Each mandala is unique and created just for you!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()