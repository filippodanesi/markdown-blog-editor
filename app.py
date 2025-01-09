import streamlit as st
import streamlit.components.v1 as components
import yaml
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import re

def init_session_state():
    """Initialize session state variables"""
    if 'markdown_text' not in st.session_state:
        st.session_state.markdown_text = ''
    if 'frontmatter' not in st.session_state:
        st.session_state.frontmatter = {
            'title': '',
            'excerpt': '',
            'publishDate': datetime.now().strftime('%Y-%m-%d'),
            'tags': [],
            'seo': {
                'image': {
                    'src': '',
                    'alt': ''
                }
            }
        }
    if 'show_image_dialog' not in st.session_state:
        st.session_state.show_image_dialog = False
    if 'image_type' not in st.session_state:
        st.session_state.image_type = None

def slugify(text):
    """Convert title to filename slug"""
    text = text.replace('"', '').replace("'", '').lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def generate_frontmatter():
    """Generate YAML frontmatter"""
    return f"""---
{yaml.dump(st.session_state.frontmatter, allow_unicode=True, sort_keys=False)}---

"""

def update_preview():
    """Update the markdown preview"""
    html = markdown.markdown(st.session_state.markdown_text, extensions=['extra'])
    soup = BeautifulSoup(html, 'html.parser')
    return str(soup)

def parse_unsplash_html(html_content):
    """Parse Unsplash HTML caption and extract components"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        img = soup.find('img')
        if not img:
            return None

        # Extract image details
        img_src = img.get('src', '')
        img_alt = img.get('alt', '')
        
        # Find photographer and source links
        links = soup.find_all('a')
        if len(links) < 2:
            return None

        photographer_link = links[0]
        source_link = links[1]
        
        # Extract UTM parameters if they exist
        utm_params = '?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash'
        photographer_url = photographer_link['href']
        if '?' not in photographer_url:
            photographer_url += utm_params
        
        source_url = source_link['href']
        if '?' not in source_url:
            source_url += utm_params

        return {
            'src': img_src,
            'alt': img_alt,
            'photographer': photographer_link.text,
            'photographer_url': photographer_url,
            'source_url': source_url
        }
    except Exception as e:
        st.error(f"Error parsing HTML: {str(e)}")
        return None

def show_image_dialog():
    """Show dialog for adding images"""
    with st.sidebar:
        if st.session_state.image_type == 'cover':
            st.subheader("Add Cover Image")
            st.info("Paste the Unsplash caption HTML here")
            html_input = st.text_area("HTML from Unsplash", height=150)
            
            if html_input:
                image_data = parse_unsplash_html(html_input)
                if image_data:
                    figure_html = f"""<figure>
  <img id="cover-img" src="{image_data['src']}" alt="{image_data['alt']}">
  <figcaption>Photo by <a href="{image_data['photographer_url']}">{image_data['photographer']}</a> on <a href="{image_data['source_url']}">Unsplash</a></figcaption>
</figure>
"""
                    if st.button("Insert Cover Image"):
                        st.session_state.markdown_text = figure_html + "\n\n" + st.session_state.markdown_text
                        st.session_state.frontmatter['seo']['image']['src'] = image_data['src']
                        st.session_state.frontmatter['seo']['image']['alt'] = image_data['alt']
                        st.session_state.show_image_dialog = False
                        st.rerun()

        elif st.session_state.image_type == 'article':
            st.subheader("Add Article Image")
            img_path = st.text_input("Image Path", placeholder="/chart-image.jpg")
            img_alt = st.text_input("Alt Text (Detailed description)", placeholder="A chart showing...")
            caption = st.text_input("Caption", placeholder="Chart title or short description")
            source_name = st.text_input("Source Name", placeholder="Organization name")
            source_url = st.text_input("Source URL", placeholder="https://source.com/data")
            author = st.text_input("Author (optional)", placeholder="Author name")
            
            if st.button("Insert Article Image"):
                author_text = f", by {author}" if author else ""
                figure_html = f"""<figure>
  <img id="article-img" src="{img_path}" alt="{img_alt}">
  <figcaption>"{caption}" \\ Source: <a href="{source_url}" target="_blank">{source_name}</a>{author_text}</figcaption>
</figure>
"""
                st.session_state.markdown_text += "\n\n" + figure_html + "\n"
                st.session_state.show_image_dialog = False
                st.rerun()

def setup_tinymce():
    """Setup TinyMCE editor component"""
    tinymce_html = """
    <html>
        <head>
            <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
            <script>
                tinymce.init({
                    selector: '#editor',
                    height: 700,
                    menubar: false,
                    plugins: 'lists link code markdown',
                    toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link | code | markdown',
                    content_style: 'body { font-family:Arial,sans-serif; font-size:16px }',
                    markdown_output: true
                });
            </script>
        </head>
        <body>
            <textarea id="editor"></textarea>
        </body>
    </html>
    """
    components.html(tinymce_html, height=750)

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    init_session_state()

    # Top bar with title input and buttons
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        title = st.text_input("Post Title", value=st.session_state.frontmatter['title'])
        if title:
            st.session_state.frontmatter['title'] = title

    with col2:
        if st.button("🖼️ Add Cover Image"):
            st.session_state.show_image_dialog = True
            st.session_state.image_type = 'cover'
            
    with col3:
        if st.button("📊 Add Article Image"):
            st.session_state.show_image_dialog = True
            st.session_state.image_type = 'article'
            
    with col4:
        if st.session_state.frontmatter['title']:
            complete_post = generate_frontmatter() + "\n" + st.session_state.markdown_text
            filename = slugify(st.session_state.frontmatter['title']) + '.md'
            st.download_button("📥 Export", complete_post, file_name=filename, mime="text/markdown")

    # Show image dialog if active
    if st.session_state.show_image_dialog:
        show_image_dialog()

    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Editor")
        setup_tinymce()
    
    with col2:
        st.markdown("### Preview")
        st.markdown(update_preview(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
