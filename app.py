import streamlit as st
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

def generate_frontmatter():
    """Generate YAML frontmatter"""
    return f"""---
{yaml.dump(st.session_state.frontmatter, allow_unicode=True, sort_keys=False)}---

"""

def slugify(text):
    """Convert title to filename slug"""
    # Remove quotes and lowercase
    text = text.replace('"', '').replace("'", '').lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def update_preview():
    """Update the markdown preview"""
    # Convert markdown to HTML
    html = markdown.markdown(st.session_state.markdown_text, extensions=['extra'])
    
    # Wrap images in figure tags with captions
    soup = BeautifulSoup(html, 'html.parser')
    for img in soup.find_all('img'):
        # Create figure element
        figure = soup.new_tag('figure')
        img.wrap(figure)
        
        # Add figcaption if alt text exists
        if img.get('alt'):
            figcaption = soup.new_tag('figcaption')
            figcaption.string = img.get('alt')
            figure.append(figcaption)
    
    return str(soup)

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor")
    init_session_state()

    st.title("Blog Editor")

    # Sidebar for frontmatter configuration
    with st.sidebar:
        st.header("Frontmatter Configuration")
        
        st.session_state.frontmatter['title'] = st.text_input(
            "Title",
            value=st.session_state.frontmatter['title']
        )
        
        st.session_state.frontmatter['excerpt'] = st.text_area(
            "Excerpt",
            value=st.session_state.frontmatter['excerpt']
        )
        
        tags = st.text_input(
            "Tags (comma-separated)",
            value=','.join(st.session_state.frontmatter['tags'])
        )
        st.session_state.frontmatter['tags'] = [tag.strip() for tag in tags.split(',') if tag]
        
        st.session_state.frontmatter['publishDate'] = st.date_input(
            "Publish Date",
            value=datetime.strptime(st.session_state.frontmatter['publishDate'], '%Y-%m-%d')
        ).strftime('%Y-%m-%d')

        # SEO Image configuration
        st.subheader("SEO Image")
        st.session_state.frontmatter['seo']['image']['src'] = st.text_input(
            "Image Source",
            value=st.session_state.frontmatter['seo']['image']['src']
        )
        st.session_state.frontmatter['seo']['image']['alt'] = st.text_input(
            "Image Alt Text",
            value=st.session_state.frontmatter['seo']['image']['alt']
        )

    # Main content area with split view
    col1, col2 = st.columns(2)

    # Markdown Editor
    with col1:
        st.header("Markdown Editor")
        
        # Add quick formatting buttons
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        with col_btn1:
            if st.button("Add H2"):
                st.session_state.markdown_text += "\n## New Heading"
        with col_btn2:
            if st.button("Add Link"):
                st.session_state.markdown_text += "\n[Link Text](url)"
        with col_btn3:
            if st.button("Add Cover Image"):
                st.session_state.markdown_text += "\n\n<figure>\n  <img id=\"cover-img\" src=\"/path-to-image.jpg\" alt=\"Image description\">\n  <figcaption>Photo by <a href=\"#\">Author</a> on <a href=\"#\">Source</a></figcaption>\n</figure>\n"
        with col_btn4:
            if st.button("Add Article Image"):
                st.session_state.markdown_text += "\n\n<figure>\n  <img id=\"article-img\" src=\"/path-to-image.jpg\" alt=\"Image description\">\n  <figcaption>\"Image caption\" \\ Source: <a href=\"#\" target=\"_blank\">Source Name</a></figcaption>\n</figure>\n"
        
        # Main editor
        st.session_state.markdown_text = st.text_area(
            "Edit your content here",
            value=st.session_state.markdown_text,
            height=600
        )

    # Preview
    with col2:
        st.header("Preview")
        
        # Show frontmatter
        with st.expander("Show Frontmatter", expanded=True):
            st.code(generate_frontmatter(), language='yaml')
        
        # Show rendered markdown
        st.markdown(update_preview(), unsafe_allow_html=True)

    # Export button
    if st.button("Export Blog Post"):
        complete_post = generate_frontmatter() + "\n" + st.session_state.markdown_text
        # Generate filename from title
        filename = slugify(st.session_state.frontmatter['title']) + '.md'
        st.download_button(
            "Download .md file",
            complete_post,
            file_name=filename,
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()
