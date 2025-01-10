import streamlit as st
import streamlit.components.v1 as components
import yaml
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import re

def init_session_state():
    """Initialize session state variables"""
    if 'content' not in st.session_state:
        st.session_state.content = ''
    if 'frontmatter' not in st.session_state:
        st.session_state.frontmatter = {
            'title': '',
            'excerpt': '',
            'publishDate': datetime.now().strftime('%Y-%m-%d'),
            'tags': [],
            'seo': {'image': {'src': '', 'alt': ''}}
        }

def parse_unsplash_html(html_content):
    """Parse Unsplash HTML and extract relevant information"""
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

def convert_markdown(content):
    """Convert markdown to HTML with proper formatting"""
    try:
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty'
        ]
        
        html = markdown.markdown(content, extensions=extensions)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process figures if they exist
        for figure in soup.find_all('figure'):
            if figure.figcaption:
                caption_html = str(figure.figcaption).replace('&lt;', '<').replace('&gt;', '>')
                figure.figcaption.replace_with(BeautifulSoup(caption_html, 'html.parser').figcaption)
        
        return str(soup)
    except Exception as e:
        st.error(f"Error converting markdown: {str(e)}")
        return content

def create_editor():
    """Create the custom editor component with toolbar"""
    editor_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .editor-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                font-family: system-ui, -apple-system, sans-serif;
            }
            .toolbar {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
                padding: 5px;
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .toolbar-group {
                display: flex;
                gap: 5px;
                padding: 0 5px;
                border-right: 1px solid #ddd;
            }
            button {
                padding: 5px 10px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            button:hover {
                background: #f0f0f0;
            }
            #editor {
                width: 100%;
                height: 600px;
                padding: 10px;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 14px;
                line-height: 1.5;
                border: 1px solid #ddd;
                border-radius: 4px;
                resize: vertical;
            }
        </style>
    </head>
    <body>
        <div class="editor-container">
            <div class="toolbar">
                <div class="toolbar-group">
                    <button onclick="insertHeading(1)" title="Heading 1">H1</button>
                    <button onclick="insertHeading(2)" title="Heading 2">H2</button>
                    <button onclick="insertHeading(3)" title="Heading 3">H3</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="insertFormat('bold')" title="Bold">B</button>
                    <button onclick="insertFormat('italic')" title="Italic">I</button>
                    <button onclick="insertFormat('code')" title="Code">`</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="insertList('unordered')" title="Bullet List">•</button>
                    <button onclick="insertList('ordered')" title="Numbered List">1.</button>
                    <button onclick="insertLink()" title="Insert Link">🔗</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="insertImage('cover')" title="Cover Image">🖼️</button>
                    <button onclick="insertImage('article')" title="Article Image">📊</button>
                </div>
            </div>
            <textarea id="editor" spellcheck="true">{st.session_state.content}</textarea>
        </div>

        <script>
            const editor = document.getElementById('editor');
            
            editor.addEventListener('input', () => {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: editor.value
                }, '*');
            });

            function getSelection() {
                return {
                    text: editor.value.substring(editor.selectionStart, editor.selectionEnd),
                    start: editor.selectionStart,
                    end: editor.selectionEnd
                };
            }

            function insertAtCursor(text) {
                const { start, end } = getSelection();
                editor.value = editor.value.substring(0, start) + 
                             text + 
                             editor.value.substring(end);
                
                editor.focus();
                const newPos = start + text.length;
                editor.setSelectionRange(newPos, newPos);
                editor.dispatchEvent(new Event('input'));
            }

            function insertHeading(level) {
                const { text } = getSelection();
                const prefix = '#'.repeat(level) + ' ';
                insertAtCursor(text ? prefix + text + '\\n' : prefix);
            }

            function insertFormat(type) {
                const { text } = getSelection();
                let formatted = '';
                
                switch(type) {
                    case 'bold':
                        formatted = `**${text || 'bold text'}**`;
                        break;
                    case 'italic':
                        formatted = `*${text || 'italic text'}*`;
                        break;
                    case 'code':
                        formatted = text.includes('\\n') 
                            ? `\`\`\`\\n${text || 'code'}\\n\`\`\`` 
                            : `\`${text || 'code'}\``;
                        break;
                }
                
                insertAtCursor(formatted);
            }

            function insertList(type) {
                const { text } = getSelection();
                let formatted = '';
                
                if (text) {
                    const lines = text.split('\\n');
                    formatted = lines
                        .filter(line => line.trim())
                        .map((line, i) => type === 'ordered' 
                            ? `${i + 1}. ${line}` 
                            : `- ${line}`)
                        .join('\\n') + '\\n';
                } else {
                    formatted = type === 'ordered' ? '1. ' : '- ';
                }
                
                insertAtCursor(formatted);
            }

            function insertLink() {
                const { text } = getSelection();
                const url = prompt('Enter URL:');
                if (url) {
                    const linkText = text || prompt('Enter link text:') || 'link text';
                    insertAtCursor(`[${linkText}](${url})`);
                }
            }

            function insertImage(type) {
                const dialogType = type === 'cover' ? 'cover-image' : 'article-image';
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: { dialog: dialogType }
                }, '*');
            }
        </script>
    </body>
    </html>
    """
    
    return components.html(editor_html, height=700)

def show_image_dialog(image_type):
    """Show dialog for adding images"""
    with st.sidebar:
        if image_type == 'cover':
            st.markdown("### Add Cover Image")
            html = st.text_area("Paste Unsplash HTML")
            
            if html:
                data = parse_unsplash_html(html)
                if data:
                    figure = f"""<figure>
  <img id="cover-img" src="{data['src']}" alt="{data['alt']}">
  <figcaption>Photo by <a href="{data['photographer_url']}">{data['photographer']}</a> on <a href="{data['source_url']}">Unsplash</a></figcaption>
</figure>\n\n"""
                    
                    st.session_state.content += figure
                    st.session_state.frontmatter['seo']['image'].update({
                        'src': data['src'],
                        'alt': data['alt']
                    })
                    st.rerun()
        
        else:  # article image
            st.markdown("### Add Article Image")
            path = st.text_input("Image Path")
            alt = st.text_input("Alt Text")
            caption = st.text_input("Caption")
            source = st.text_input("Source Name")
            url = st.text_input("Source URL")
            author = st.text_input("Author (optional)")
            
            if st.button("Insert") and all([path, alt, caption, source, url]):
                author_text = f", by {author}" if author else ""
                figure = f"""<figure>
  <img id="article-img" src="{path}" alt="{alt}">
  <figcaption>"{caption}" \\ Source: <a href="{url}" target="_blank">{source}</a>{author_text}</figcaption>
</figure>\n\n"""
                
                st.session_state.content += figure
                st.rerun()

def main():
    """Main application function"""
    st.set_page_config(layout="wide", page_title="Markdown Blog Editor", page_icon="📝")
    init_session_state()

    # Title bar
    st.title("📝 Markdown Blog Editor")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        title = st.text_input("Post Title", value=st.session_state.frontmatter['title'])
        if title != st.session_state.frontmatter['title']:
            st.session_state.frontmatter['title'] = title
            
    with col2:
        tags = st.text_input(
            "Tags (comma-separated)", 
            value=','.join(st.session_state.frontmatter.get('tags', []))
        )
        st.session_state.frontmatter['tags'] = [
            tag.strip() for tag in tags.split(',') if tag.strip()
        ]
    
    with col3:
        if st.session_state.frontmatter['title']:
            complete_post = f"""---
{yaml.dump(st.session_state.frontmatter, allow_unicode=True, sort_keys=False)}---

{st.session_state.content}"""
            filename = re.sub(r'[^a-z0-9]+', '-', title.lower()) + '.md'
            st.download_button("📥 Export", complete_post, filename, 
                             "text/markdown", use_container_width=True)

    # Main editor and preview
    col1, col2 = st.columns(2)
    
    with col1:
        create_editor()

    with col2:
        st.markdown("### Preview")
        st.markdown(convert_markdown(st.session_state.content), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
