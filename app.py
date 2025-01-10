import streamlit as st
import yaml
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import re

class MarkdownEditor:
    def __init__(self):
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'content' not in st.session_state:
            st.session_state.content = ''
        if 'cursor_position' not in st.session_state:
            st.session_state.cursor_position = 0
        if 'show_popup' not in st.session_state:
            st.session_state.show_popup = False
        if 'popup_type' not in st.session_state:
            st.session_state.popup_type = None
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

    def parse_unsplash_html(self, html_content):
        """Parse Unsplash HTML and return structured data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        img = soup.find('img')
        links = soup.find_all('a')
        
        if img and len(links) >= 2:
            utm_params = '?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash'
            return {
                'src': img['src'],
                'alt': img.get('alt', ''),
                'photographer': links[0].text,
                'photographer_url': links[0]['href'] + ('' if '?' in links[0]['href'] else utm_params),
                'source_url': links[1]['href'] + ('' if '?' in links[1]['href'] else utm_params)
            }
        return None

    def insert_at_cursor(self, text):
        """Insert text at current cursor position"""
        pos = st.session_state.cursor_position
        current = st.session_state.content
        st.session_state.content = current[:pos] + text + current[pos:]

    def show_insert_menu(self):
        """Show the insert dropdown menu"""
        options = {
            'Cover Image': '🖼️',
            'Article Image': '📊',
            'Heading 2': '##',
            'Heading 3': '###',
            'Bold Text': '**',
            'Italic Text': '*',
            'Link': '🔗',
            'Blockquote': '>',
            'Code Block': '```',
            'List': '•'
        }
        
        selected = st.selectbox(
            "Insert",
            options.keys(),
            format_func=lambda x: f"{options[x]} {x}",
            label_visibility="collapsed"
        )
        
        if selected:
            st.session_state.show_popup = True
            st.session_state.popup_type = selected
            st.rerun()

    def show_popup(self):
        """Show popup based on selected type"""
        with st.sidebar:
            if st.session_state.popup_type == 'Cover Image':
                self.show_cover_image_popup()
            elif st.session_state.popup_type == 'Article Image':
                self.show_article_image_popup()
            elif st.session_state.popup_type == 'Link':
                self.show_link_popup()
            else:
                self.insert_markdown_element()
            
            if st.button("Cancel"):
                st.session_state.show_popup = False
                st.session_state.popup_type = None
                st.rerun()

    def update_frontmatter(self, **kwargs):
        """Update frontmatter with provided key-value pairs"""
        for key, value in kwargs.items():
            if '.' in key:  # Handle nested keys like 'seo.image.src'
                parts = key.split('.')
                target = st.session_state.frontmatter
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value
            else:
                st.session_state.frontmatter[key] = value
    
    def show_cover_image_popup(self):
        """Popup for cover image insertion"""
        st.markdown("### Insert Cover Image")
        
        # File path and alt text
        path = st.text_input("Image Path", placeholder="/your-image.webp")
        alt = st.text_input("Alt Text", placeholder="Descriptive text for the image")
        
        # Unsplash HTML credit
        st.markdown("#### Unsplash Credit")
        html = st.text_area(
            "Paste Unsplash caption HTML here",
            height=100,
            help="Copy the entire caption HTML from Unsplash"
        )
        
        if st.button("Insert"):
            # Parse Unsplash HTML if provided
            if html.strip():
                data = self.parse_unsplash_html(html)
                if data:
                    path = data['src']
                    alt = data['alt']
                    caption = f'Photo by <a href="{data["photographer_url"]}">{data["photographer"]}</a> on <a href="{data["source_url"]}">Unsplash</a>'
                else:
                    st.error("Invalid Unsplash HTML format")
                    return
            else:
                caption = "Image caption"
            
            # Update frontmatter with image details
            self.update_frontmatter(**{
                'seo.image.src': path,
                'seo.image.alt': alt,
                'cover_image': {
                    'src': path,
                    'alt': alt,
                    'caption': caption
                }
            })
            
            # Generate figure HTML
            figure = f"""<figure>
  <img id="cover-img" src="{path}" alt="{alt}">
  <figcaption>{caption}</figcaption>
</figure>\n\n"""
            
            self.insert_at_cursor(figure)
            st.session_state.show_popup = False
            st.rerun()

    def show_article_image_popup(self):
        """Popup for article image insertion"""
        st.markdown("### Insert Article Image")
        
        # File path and alt text
        path = st.text_input("Image Path", placeholder="/your-article-image.jpg")
        alt = st.text_input("Alt Text", placeholder="Detailed description of the image")
        
        # Source information
        source_name = st.text_input("Source Name", placeholder="Organization name")
        source_url = st.text_input("Source URL", placeholder="https://source.com/...")
        author = st.text_input("Author (optional)", placeholder="Author name")
        caption = st.text_input("Caption", placeholder="Chart or image title")
        
        if st.button("Insert"):
            author_text = f", by {author}" if author else ""
            full_caption = f'"{caption}" \\ Source: <a href="{source_url}" target="_blank">{source_name}</a>{author_text}'
            
            # Update frontmatter
            image_data = {
                'src': path,
                'alt': alt,
                'caption': caption,
                'source': {
                    'name': source_name,
                    'url': source_url
                }
            }
            if author:
                image_data['author'] = author
            
            # If article_images doesn't exist in frontmatter, create it
            if 'article_images' not in st.session_state.frontmatter:
                st.session_state.frontmatter['article_images'] = []
            st.session_state.frontmatter['article_images'].append(image_data)
            
            # Generate figure HTML
            figure = f"""<figure>
  <img id="article-img" src="{path}" alt="{alt}">
  <figcaption>{full_caption}</figcaption>
</figure>\n\n"""
            
            self.insert_at_cursor(figure)
            st.session_state.show_popup = False
            st.rerun()

    def show_link_popup(self):
        """Popup for link insertion"""
        st.markdown("### Insert Link")
        text = st.text_input("Link Text", placeholder="Click here")
        url = st.text_input("URL", placeholder="https://...")
        
        if st.button("Insert"):
            self.insert_at_cursor(f"[{text}]({url})")
            st.session_state.show_popup = False
            st.rerun()

    def insert_markdown_element(self):
        """Insert markdown elements based on type"""
        element_map = {
            'Heading 2': '\n## ',
            'Heading 3': '\n### ',
            'Bold Text': '**bold text**',
            'Italic Text': '*italic text*',
            'Blockquote': '\n> ',
            'Code Block': '\n```\ncode\n```\n',
            'List': '\n- Item 1\n- Item 2\n- Item 3\n'
        }
        
        if st.session_state.popup_type in element_map:
            self.insert_at_cursor(element_map[st.session_state.popup_type])
            st.session_state.show_popup = False
            st.rerun()

    def render(self):
        """Render the main editor interface"""
        # Top bar with title and insert menu
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.session_state.frontmatter['title'] = st.text_input(
                "Title", 
                value=st.session_state.frontmatter['title'],
                placeholder="Enter post title..."
            )
        with col2:
            self.show_insert_menu()
        with col3:
            if st.session_state.frontmatter['title']:
                filename = st.session_state.frontmatter['title'].lower().replace(' ', '-') + '.md'
                content = generate_frontmatter(st.session_state.frontmatter) + "\n" + st.session_state.content
                st.download_button("📥 Export", content, filename, "text/markdown", use_container_width=True)

        # Show popup if needed
        if st.session_state.show_popup:
            self.show_popup()

        # Main editor area
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Editor")
            # Track cursor position with callback
            text_area = st.empty()
            new_content = text_area.text_area(
                "Edit your content here",
                st.session_state.content,
                label_visibility="collapsed",
                height=700,
                key="editor"
            )
            if new_content != st.session_state.content:
                st.session_state.content = new_content
        
        with col2:
            st.markdown("### Preview")
            preview_content = markdown.markdown(st.session_state.content, extensions=['extra'])
            st.markdown(preview_content, unsafe_allow_html=True)

def generate_frontmatter(data):
    """Generate YAML frontmatter"""
    return f"""---
{yaml.dump(data, allow_unicode=True, sort_keys=False)}---"""

def main():
    st.set_page_config(layout="wide", page_title="Blog Editor", page_icon="📝")
    editor = MarkdownEditor()
    editor.render()

if __name__ == "__main__":
    main()
