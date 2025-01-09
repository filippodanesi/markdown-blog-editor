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
    if 'show_cover_dialog' not in st.session_state:
        st.session_state.show_cover_dialog = False
    if 'show_article_dialog' not in st.session_state:
        st.session_state.show_article_dialog = False
    if 'unsplash_html' not in st.session_state:
        st.session_state.unsplash_html = ''

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
        if not img.parent.name == 'figure':
            figure = soup.new_tag('figure')
            img.wrap(figure)
            if img.get('alt'):
                figcaption = soup.new_tag('figcaption')
                figcaption.string = img.get('alt')
                figure.append(figcaption)
    return str(soup)

def parse_unsplash_html(html_content):
    """Parse Unsplash HTML caption and extract components"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the image
    img = soup.find('img')
    if img:
        img_src = img.get('src', '')
        img_alt = img.get('alt', '')
    else:
        return None
        
    # Find photographer and source links
    links = soup.find_all('a')
    if len(links) >= 2:
        photographer = links[0].text
        photographer_url = links[0]['href']
        source_url = links[1]['href']
        return {
            'src': img_src,
            'alt': img_alt,
            'photographer': photographer,
            'photographer_url': photographer_url,
            'source_url': source_url
        }
    return None

def show_cover_dialog():
    """Show dialog for adding cover image"""
    with st.sidebar:
        st.subheader("Add Cover Image")
        st.markdown("Paste the Unsplash caption HTML here:")
        
        # HTML input
        html_input = st.text_area("HTML from Unsplash", height=150)
        if html_input:
            image_data = parse_unsplash_html(html_input)
            if image_data:
                figure_html = f"""
<figure>
  <img id="cover-img" src="{image_data['src']}" alt="{image_data['alt']}">
  <figcaption>Photo by <a href="{image_data['photographer_url']}">{image_data['photographer']}</a> on <a href="{image_data['source_url']}">Unsplash</a></figcaption>
</figure>
"""
                if st.button("Insert Cover Image"):
                    st.session_state.markdown_text += figure_html
                    st.session_state.frontmatter['seo']['image']['src'] = image_data['src']
                    st.session_state.frontmatter['seo']['image']['alt'] = image_data['alt']
                    st.session_state.show_cover_dialog = False
                    st.rerun()
            else:
                st.error("Invalid HTML format. Please copy the entire caption from Unsplash.")

def show_article_dialog():
    """Show dialog for adding article image"""
    with st.sidebar:
        st.subheader("Add Article Image")
        
        # Input fields
        col1, col2 = st.columns(2)
        with col1:
            img_path = st.text_input("Image Path", placeholder="/your-article-image.jpg")
            img_alt = st.text_input("Alt Text", placeholder="Chart or figure description")
        with col2:
            caption = st.text_input("Caption", placeholder="Chart title or description")
            source_name = st.text_input("Source", placeholder="Source Organization")
            source_url = st.text_input("URL", placeholder="https://source.com/data")
        
        if st.button("Insert Article Image"):
            figure_html = f"""
<figure>
  <img id="article-img" src="{img_path}" alt="{img_alt}">
  <figcaption>"{caption}" \\ Source: <a href="{source_url}" target="_blank">{source_name}</a></figcaption>
</figure>
"""
            st.session_state.markdown_text += figure_html
            st.session_state.show_article_dialog = False
            st.rerun()

def render_toolbar():
    """Render the formatting toolbar"""
    cols = st.columns([2,2,2,3])
    
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
        if st.button("[Link]"):
            st.session_state.markdown_text += "[text](url)"
            
    # Image buttons
    with cols[2]:
        if st.button("🖼️ Cover Image"):
            st.session_state.show_cover_dialog = not st.session_state.show_cover_dialog
            st.session_state.show_article_dialog = False
        if st.button("📊 Article Image"):
            st.session_state.show_article_dialog = not st.session_state.show_article_dialog
            st.session_state.show_cover_dialog = False
            
    # Export
    with cols[3]:
        if st.session_state.frontmatter['title']:
            complete_post = generate_frontmatter() + "\n" + st.session_state.markdown_text
            filename = slugify(st.session_state.frontmatter['title']) + '.md'
            st.download_button(
                "📥 Export Blog Post",
                complete_post,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.text_input("Post Title", 
                         placeholder="Enter a title to enable export",
                         value=st.session_state.frontmatter['title'],
                         on_change=lambda: setattr(st.session_state.frontmatter, 'title', st.session_state.frontmatter['title']))

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    init_session_state()

    # Render toolbar
    render_toolbar()
    
    # Show dialogs if active
    if st.session_state.show_cover_dialog:
        show_cover_dialog()
    elif st.session_state.show_article_dialog:
        show_article_dialog()
        
    # Main editor and preview
    col1, col2 = st.columns(2)
    
    # Editor column
    with col1:
        st.markdown("### Editor")
        st.session_state.markdown_text = st.text_area(
            "Edit your content here",
            value=st.session_state.markdown_text,
            height=700,
            label_visibility="collapsed"
        )
    
    # Preview column
    with col2:
        st.markdown("### Preview")
        st.markdown(update_preview(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
