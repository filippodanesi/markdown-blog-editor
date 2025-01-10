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

def generate_frontmatter(data):
    """Generate YAML frontmatter"""
    return f"""---
{yaml.dump(data, allow_unicode=True, sort_keys=False)}---"""

def convert_markdown(content):
    """Convert markdown to HTML with proper handling of all elements"""
    try:
        # Use all markdown extensions for full feature support
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
            'markdown.extensions.toc'
        ]
        
        html = markdown.markdown(content, extensions=extensions)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process figures if they exist
        for figure in soup.find_all('figure'):
            # Ensure figcaption preserves HTML
            if figure.figcaption:
                caption_html = str(figure.figcaption).replace('&lt;', '<').replace('&gt;', '>')
                figure.figcaption.replace_with(BeautifulSoup(caption_html, 'html.parser').figcaption)
        
        return str(soup)
    except Exception as e:
        st.error(f"Error converting markdown: {str(e)}")
        return content

def create_editor():
    """Create the Markdown editor component"""
    editor_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .editor-container {
                display: flex;
                flex-direction: column;
                height: 100%;
                font-family: system-ui, -apple-system, sans-serif;
            }
            .toolbar {
                padding: 8px;
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px 4px 0 0;
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }
            .toolbar button {
                padding: 6px 12px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            .toolbar button:hover {
                background: #f0f0f0;
            }
            .toolbar-group {
                display: flex;
                gap: 4px;
                padding: 0 8px;
                border-right: 1px solid #ddd;
            }
            #editor {
                flex-grow: 1;
                width: 100%;
                min-height: 500px;
                padding: 12px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.5;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 4px 4px;
                resize: vertical;
            }
        </style>
    </head>
    <body>
        <div class="editor-container">
            <div class="toolbar">
                <div class="toolbar-group">
                    <button onclick="formatText('h1')" title="Heading 1">H1</button>
                    <button onclick="formatText('h2')" title="Heading 2">H2</button>
                    <button onclick="formatText('h3')" title="Heading 3">H3</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="formatText('bold')" title="Bold">B</button>
                    <button onclick="formatText('italic')" title="Italic">I</button>
                    <button onclick="formatText('code')" title="Code">`</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="formatText('link')" title="Link">🔗</button>
                    <button onclick="formatText('unorderedList')" title="Bullet List">•</button>
                    <button onclick="formatText('orderedList')" title="Numbered List">1.</button>
                </div>
                <div class="toolbar-group">
                    <button onclick="insertFigure('cover')" title="Cover Image">🖼️</button>
                    <button onclick="insertFigure('article')" title="Article Image">📊</button>
                </div>
            </div>
            <textarea id="editor" onselect="handleSelection()" onkeyup="updateContent(this.value)"></textarea>
        </div>

        <script>
            const editor = document.getElementById('editor');
            let lastSelection = { start: 0, end: 0, text: '' };

            editor.addEventListener('select', function() {
                lastSelection = {
                    start: this.selectionStart,
                    end: this.selectionEnd,
                    text: this.value.substring(this.selectionStart, this.selectionEnd)
                };
            });

            function updateContent(value) {
                window.parent.postMessage({
                    type: 'editor_content',
                    content: value
                }, '*');
            }

            function insertAtCursor(text, moveOffset = 0) {
                const start = editor.selectionStart;
                const end = editor.selectionEnd;
                
                editor.value = editor.value.substring(0, start) + 
                             text + 
                             editor.value.substring(end);
                
                // Set cursor position
                const newPos = start + text.length + moveOffset;
                editor.focus();
                editor.setSelectionRange(newPos, newPos);
                
                updateContent(editor.value);
            }

            function formatText(type) {
                const selectedText = lastSelection.text;
                let formattedText = '';
                let cursorOffset = 0;

                switch(type) {
                    case 'h1':
                        formattedText = selectedText ? `# ${selectedText}` : '# ';
                        break;
                    case 'h2':
                        formattedText = selectedText ? `## ${selectedText}` : '## ';
                        break;
                    case 'h3':
                        formattedText = selectedText ? `### ${selectedText}` : '### ';
                        break;
                    case 'bold':
                        formattedText = `**${selectedText || 'bold text'}**`;
                        cursorOffset = selectedText ? 0 : -2;
                        break;
                    case 'italic':
                        formattedText = `*${selectedText || 'italic text'}*`;
                        cursorOffset = selectedText ? 0 : -1;
                        break;
                    case 'code':
                        if (selectedText.includes('\n')) {
                            formattedText = `\`\`\`\n${selectedText || 'code'}\n\`\`\``;
                        } else {
                            formattedText = `\`${selectedText || 'code'}\``;
                        }
                        break;
                    case 'link':
                        const url = prompt('Enter URL:') || '#';
                        formattedText = `[${selectedText || 'link text'}](${url})`;
                        break;
                    case 'unorderedList':
                        if (selectedText) {
                            formattedText = selectedText.split('\n')
                                .map(line => line.trim() ? `- ${line}` : '')
                                .join('\n');
                        } else {
                            formattedText = '- ';
                        }
                        break;
                    case 'orderedList':
                        if (selectedText) {
                            formattedText = selectedText.split('\n')
                                .map((line, i) => line.trim() ? `${i + 1}. ${line}` : '')
                                .join('\n');
                        } else {
                            formattedText = '1. ';
                        }
                        break;
                }

                insertAtCursor(formattedText, cursorOffset);
            }

            function insertFigure(type) {
                window.parent.postMessage({
                    type: 'insert_figure',
                    figureType: type,
                    position: editor.selectionStart
                }, '*');
            }

            // Initialize with content from Streamlit
            window.addEventListener('message', function(e) {
                if (e.data.type === 'editor_init') {
                    editor.value = e.data.content || '';
                }
            });
        </script>
    </body>
    </html>
    """
    components.html(editor_html, height=700)

def main():
    st.set_page_config(layout="wide", page_title="Markdown Blog Editor", page_icon="📝")
    init_session_state()

    # Header
    st.title("📝 Markdown Blog Editor")
    
    # Title and metadata
    col1, col2 = st.columns([3, 1])
    with col1:
        title = st.text_input("Post Title", value=st.session_state.frontmatter['title'])
        if title != st.session_state.frontmatter['title']:
            st.session_state.frontmatter['title'] = title
    
    with col2:
        if st.session_state.frontmatter['title']:
            complete_post = generate_frontmatter(st.session_state.frontmatter) + "\n\n" + st.session_state.content
            filename = re.sub(r'[^a-z0-9]+', '-', title.lower()) + '.md'
            st.download_button("📥 Export", complete_post, filename, "text/markdown", use_container_width=True)

    # Main editor and preview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Editor")
        create_editor()  # Custom editor component
        
    with col2:
        st.markdown("### Preview")
        if st.session_state.content:
            st.markdown(convert_markdown(st.session_state.content), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
