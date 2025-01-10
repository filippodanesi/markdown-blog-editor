import streamlit as st
import yaml
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import re

# Cache the markdown conversion
@st.cache_data(show_spinner=False)
def convert_markdown(content):
    """Convert markdown to HTML with caching"""
    try:
        html = markdown.markdown(content, extensions=['extra'])
        soup = BeautifulSoup(html, 'html.parser')
        return str(soup)
    except Exception as e:
        st.error(f"Error converting markdown: {str(e)}")
        return content

# Cache the frontmatter generation
@st.cache_data(show_spinner=False)
def generate_frontmatter(data):
    """Generate YAML frontmatter with caching"""
    try:
        return f"""---\n{yaml.dump(data, allow_unicode=True, sort_keys=False)}---"""
    except Exception as e:
        st.error(f"Error generating frontmatter: {str(e)}")
        return ""

def parse_unsplash_html(html_content):
    """Parse Unsplash HTML without re-parsing on every update"""
    if not html_content:
        return None
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        img = soup.find('img')
        links = soup.find_all('a')
        
        if not (img and len(links) >= 2):
            return None

        utm_params = '?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash'
        
        return {
            'src': img['src'],
            'alt': img.get('alt', ''),
            'photographer': links[0].text,
            'photographer_url': links[0]['href'] + ('' if '?' in links[0]['href'] else utm_params),
            'source_url': links[1]['href'] + ('' if '?' in links[1]['href'] else utm_params)
        }
    except Exception:
        return None

def initialize_state():
    """Initialize session state only if needed"""
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'content': '',
            'frontmatter': {
                'title': '',
                'excerpt': '',
                'publishDate': datetime.now().strftime('%Y-%m-%d'),
                'tags': [],
                'seo': {'image': {'src': '', 'alt': ''}}
            },
            'show_popup': False,
            'popup_type': None,
            'initialized': True
        })

def insert_figure(figure_type, data):
    """Insert figure HTML at current position"""
    if figure_type == 'cover':
        figure = f"""<figure>
  <img id="cover-img" src="{data['src']}" alt="{data['alt']}">
  <figcaption>{data['caption']}</figcaption>
</figure>\n\n"""
        
        # Update frontmatter
        st.session_state.frontmatter['seo']['image'].update({
            'src': data['src'],
            'alt': data['alt']
        })
        
    else:  # article
        author_text = f", by {data['author']}" if data.get('author') else ""
        figure = f"""<figure>
  <img id="article-img" src="{data['src']}" alt="{data['alt']}">
  <figcaption>"{data['caption']}" \\ Source: <a href="{data['source_url']}" target="_blank">{data['source_name']}</a>{author_text}</figcaption>
</figure>\n\n"""
        
        # Update frontmatter
        if 'article_images' not in st.session_state.frontmatter:
            st.session_state.frontmatter['article_images'] = []
        st.session_state.frontmatter['article_images'].append({
            'src': data['src'],
            'alt': data['alt'],
            'caption': data['caption'],
            'source': {
                'name': data['source_name'],
                'url': data['source_url']
            }
        })

    # Insert at current cursor position or at the end
    current = st.session_state.content
    st.session_state.content = current + figure

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    initialize_state()

    # Top bar
    col1, col2 = st.columns([4, 1])
    with col1:
        title = st.text_input("Title", value=st.session_state.frontmatter['title'])
        if title != st.session_state.frontmatter['title']:
            st.session_state.frontmatter['title'] = title
    
    with col2:
        if st.session_state.frontmatter['title']:
            complete_post = (generate_frontmatter(st.session_state.frontmatter) + 
                           "\n" + st.session_state.content)
            filename = re.sub(r'[^a-z0-9]+', '-', title.lower()) + '.md'
            st.download_button("📥 Export", complete_post, filename, 
                             "text/markdown", use_container_width=True)

    # Insert menu
    insert_options = {
        'Cover Image from Unsplash': lambda: show_cover_dialog(),
        'Article Image': lambda: show_article_dialog(),
        'Basic Elements': lambda: show_basic_elements()
    }
    
    selected = st.selectbox("Insert", options=list(insert_options.keys()),
                          label_visibility="collapsed")
    if selected:
        insert_options[selected]()

    # Main editor
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Editor")
        content = st.text_area("Content", value=st.session_state.content,
                             height=600, label_visibility="collapsed",
                             key="editor")
        if content != st.session_state.content:
            st.session_state.content = content

    with col2:
        st.markdown("### Preview")
        preview = convert_markdown(st.session_state.content)
        st.markdown(preview, unsafe_allow_html=True)

def show_cover_dialog():
    with st.sidebar:
        st.markdown("### Add Cover Image")
        st.info("Paste Unsplash HTML or enter details manually")
        
        html = st.text_area("Unsplash HTML")
        
        if html:
            data = parse_unsplash_html(html)
            if data:
                insert_figure('cover', {
                    'src': data['src'],
                    'alt': data['alt'],
                    'caption': f'Photo by <a href="{data["photographer_url"]}">{data["photographer"]}</a> on <a href="{data["source_url"]}">Unsplash</a>'
                })
                st.success("Cover image added!")
                return

        # Manual input as fallback
        path = st.text_input("Image Path")
        alt = st.text_input("Alt Text")
        if path and alt:
            insert_figure('cover', {
                'src': path,
                'alt': alt,
                'caption': 'Image caption'
            })
            st.success("Cover image added!")

def show_article_dialog():
    with st.sidebar:
        st.markdown("### Add Article Image")
        
        path = st.text_input("Image Path")
        alt = st.text_input("Alt Text")
        caption = st.text_input("Caption")
        source_name = st.text_input("Source Name")
        source_url = st.text_input("Source URL")
        author = st.text_input("Author (optional)")
        
        if all([path, alt, caption, source_name, source_url]):
            insert_figure('article', {
                'src': path,
                'alt': alt,
                'caption': caption,
                'source_name': source_name,
                'source_url': source_url,
                'author': author
            })
            st.success("Article image added!")

def show_basic_elements():
    with st.sidebar:
        st.markdown("### Add Basic Elements")
        elements = {
            'Heading 2': '\n## ',
            'Heading 3': '\n### ',
            'Bold Text': '**bold text**',
            'Italic Text': '*italic text*',
            'Link': '[text](url)',
            'List': '\n- Item 1\n- Item 2\n- Item 3\n',
            'Code Block': '\n```\ncode\n```\n'
        }
        
        for name, content in elements.items():
            if st.button(name):
                st.session_state.content += content

if __name__ == "__main__":
    main()
