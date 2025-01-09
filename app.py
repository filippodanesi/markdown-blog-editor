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
    if 'show_frontmatter' not in st.session_state:
        st.session_state.show_frontmatter = False
    if 'show_images' not in st.session_state:
        st.session_state.show_images = False

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
    # If frontmatter is enabled, include it in the preview
    content = st.session_state.markdown_text
    if st.session_state.show_frontmatter:
        content = generate_frontmatter() + "\n" + content
    
    html = markdown.markdown(content, extensions=['extra'])
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
        st.session_state.show_images = False
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
        st.session_state.show_images = False
        st.success("Article image added!")

def render_toolbar():
    """Render the formatting toolbar"""
    cols = st.columns([1,1,1,2,1])
    
    # Basic formatting
    with cols[0]:
        if st.button("# H1"):
            st.session_state.markdown_text += "\n# "
        if st.button("## H2"):
            st.session_state.markdown_text += "\n## "
        if st.button("### H3"):
            st.session_state.markdown_text += "\n### "
            
    with cols[1]:
        if st.button("**Bold**"):
            st.session_state.markdown_text += "**bold text**"
        if st.button("*Italic*"):
            st.session_state.markdown_text += "*italic text*"
        if st.button("`Code`"):
            st.session_state.markdown_text += "`code`"
            
    with cols[2]:
        if st.button("List"):
            st.session_state.markdown_text += "\n- Item 1\n- Item 2\n- Item 3"
        if st.button("Numbers"):
            st.session_state.markdown_text += "\n1. First\n2. Second\n3. Third"
        if st.button("[Link]"):
            st.session_state.markdown_text += "[text](url)"
    
    # Frontmatter and Images toggles
    with cols[3]:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.show_frontmatter = st.toggle("Show Frontmatter", st.session_state.show_frontmatter)
        with col2:
            st.session_state.show_images = st.toggle("Show Image Tools", st.session_state.show_images)
            
    # Export
    with cols[4]:
        if st.session_state.frontmatter['title']:
            complete_post = generate_frontmatter() + "\n" + st.session_state.markdown_text
            filename = slugify(st.session_state.frontmatter['title']) + '.md'
            st.download_button(
                "📥 Export",
                complete_post,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )

def render_frontmatter_form():
    """Render the frontmatter configuration form"""
    with st.expander("Frontmatter Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.frontmatter['title'] = st.text_input(
                "Title",
                value=st.session_state.frontmatter['title']
            )
            
            st.session_state.frontmatter['excerpt'] = st.text_area(
                "Excerpt",
                value=st.session_state.frontmatter['excerpt'],
                height=100
            )
        
        with col2:
            tags = st.text_input(
                "Tags (comma-separated)",
                value=','.join(st.session_state.frontmatter['tags'])
            )
            st.session_state.frontmatter['tags'] = [tag.strip() for tag in tags.split(',') if tag]
            
            st.session_state.frontmatter['publishDate'] = st.date_input(
                "Publish Date",
                value=datetime.strptime(st.session_state.frontmatter['publishDate'], '%Y-%m-%d')
            ).strftime('%Y-%m-%d')

def render_image_tools():
    """Render the image management tools"""
    with st.expander("Image Management", expanded=True):
        tab1, tab2 = st.tabs(["Cover Image", "Article Image"])
        
        with tab1:
            create_cover_image()
        
        with tab2:
            create_article_image()

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    init_session_state()

    # Header and toolbar
    st.title("📝 Markdown Blog Editor")
    render_toolbar()
    
    # Conditional forms
    if st.session_state.show_frontmatter:
        render_frontmatter_form()
    if st.session_state.show_images:
        render_image_tools()
        
    # Main editor and preview
    col1, col2 = st.columns(2)
    
    # Editor column
    with col1:
        st.markdown("### Editor")
        st.session_state.markdown_text = st.text_area(
            "Edit your content here",
            value=st.session_state.markdown_text,
            height=600,
            label_visibility="collapsed"
        )
    
    # Preview column
    with col2:
        st.markdown("### Preview")
        st.markdown(update_preview(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
