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
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 'write'

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
    for img in soup.find_all('img'):
        figure = soup.new_tag('figure')
        img.wrap(figure)
        if img.get('alt'):
            figcaption = soup.new_tag('figcaption')
            figcaption.string = img.get('alt')
            figure.append(figcaption)
    return str(soup)

def create_cover_image():
    """Generate cover image HTML"""
    col1, col2 = st.columns(2)
    with col1:
        img_path = st.text_input("Cover Image Path", placeholder="/your-image.webp")
        img_alt = st.text_input("Cover Image Alt Text", placeholder="Descriptive image text")
    with col2:
        photographer = st.text_input("Photographer Name", placeholder="Photographer")
        photographer_url = st.text_input("Photographer URL", placeholder="https://unsplash.com/@photographer")
        source = st.text_input("Source Name", placeholder="Unsplash")
        source_url = st.text_input("Source URL", placeholder="https://unsplash.com/photos/...")
    
    if st.button("Insert Cover Image"):
        figure_html = f"""
<figure>
  <img id="cover-img" src="{img_path}" alt="{img_alt}">
  <figcaption>Photo by <a href="{photographer_url}">{photographer}</a> on <a href="{source_url}">{source}</a></figcaption>
</figure>
"""
        st.session_state.markdown_text += figure_html
        st.session_state.frontmatter['seo']['image']['src'] = img_path
        st.session_state.frontmatter['seo']['image']['alt'] = img_alt
        st.success("Cover image added!")

def create_article_image():
    """Generate article image HTML"""
    col1, col2 = st.columns(2)
    with col1:
        img_path = st.text_input("Article Image Path", placeholder="/your-article-image.jpg")
        img_alt = st.text_input("Article Image Alt Text", placeholder="Chart or figure description")
    with col2:
        caption = st.text_input("Image Caption", placeholder="Chart title or description")
        source_name = st.text_input("Source Name", placeholder="Source Organization")
        source_url = st.text_input("Source URL", placeholder="https://source.com/data")
    
    if st.button("Insert Article Image"):
        figure_html = f"""
<figure>
  <img id="article-img" src="{img_path}" alt="{img_alt}">
  <figcaption>"{caption}" \\ Source: <a href="{source_url}" target="_blank">{source_name}</a></figcaption>
</figure>
"""
        st.session_state.markdown_text += figure_html
        st.success("Article image added!")

def render_editor():
    """Render the main editor interface"""
    st.markdown("### Content Editor")
    
    # Quick formatting toolbar
    cols = st.columns(5)
    if cols[0].button("H2"):
        st.session_state.markdown_text += "\n## "
    if cols[1].button("H3"):
        st.session_state.markdown_text += "\n### "
    if cols[2].button("Bold"):
        st.session_state.markdown_text += "**bold text**"
    if cols[3].button("Link"):
        st.session_state.markdown_text += "[text](url)"
    if cols[4].button("List"):
        st.session_state.markdown_text += "\n- Item 1\n- Item 2\n- Item 3"
    
    # Main editor
    st.session_state.markdown_text = st.text_area(
        "Edit your content here",
        value=st.session_state.markdown_text,
        height=500
    )

def render_frontmatter():
    """Render the frontmatter configuration interface"""
    st.markdown("### Frontmatter Configuration")
    
    # Basic metadata
    st.session_state.frontmatter['title'] = st.text_input(
        "Title",
        value=st.session_state.frontmatter['title']
    )
    
    st.session_state.frontmatter['excerpt'] = st.text_area(
        "Excerpt",
        value=st.session_state.frontmatter['excerpt'],
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        tags = st.text_input(
            "Tags (comma-separated)",
            value=','.join(st.session_state.frontmatter['tags'])
        )
        st.session_state.frontmatter['tags'] = [tag.strip() for tag in tags.split(',') if tag]
    
    with col2:
        st.session_state.frontmatter['publishDate'] = st.date_input(
            "Publish Date",
            value=datetime.strptime(st.session_state.frontmatter['publishDate'], '%Y-%m-%d')
        ).strftime('%Y-%m-%d')

def render_images():
    """Render the image management interface"""
    st.markdown("### Image Management")
    
    tab1, tab2 = st.tabs(["Cover Image", "Article Image"])
    
    with tab1:
        create_cover_image()
    
    with tab2:
        create_article_image()

def render_preview():
    """Render the preview interface"""
    st.markdown("### Preview")
    
    with st.expander("Frontmatter Preview", expanded=True):
        st.code(generate_frontmatter(), language='yaml')
    
    st.markdown("### Content Preview")
    st.markdown(update_preview(), unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    init_session_state()

    # Header
    st.title("📝 Blog Post Editor")
    
    # Navigation
    sections = {
        'write': '✏️ Write',
        'frontmatter': '🔧 Frontmatter',
        'images': '🖼️ Images',
        'preview': '👁️ Preview'
    }
    
    st.session_state.current_section = st.radio(
        "Navigation",
        options=list(sections.keys()),
        format_func=lambda x: sections[x],
        horizontal=True
    )
    
    st.divider()

    # Main content area
    if st.session_state.current_section == 'write':
        render_editor()
    elif st.session_state.current_section == 'frontmatter':
        render_frontmatter()
    elif st.session_state.current_section == 'images':
        render_images()
    else:  # preview
        render_preview()
    
    # Export section (always visible)
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.frontmatter['title']:
            complete_post = generate_frontmatter() + "\n" + st.session_state.markdown_text
            filename = slugify(st.session_state.frontmatter['title']) + '.md'
            st.download_button(
                "📥 Download Blog Post",
                complete_post,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.warning("Please add a title in the Frontmatter section before exporting")

if __name__ == "__main__":
    main()
