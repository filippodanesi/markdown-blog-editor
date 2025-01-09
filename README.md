# Markdown Blog Editor

A real-time Markdown blog editor built with Streamlit, featuring frontmatter generation and image management.

## Features

- **Real-time Markdown Editor**: Split-view interface with live preview
- **YAML Frontmatter Management**: Easy configuration of blog post metadata
- **Image Management**: Quick insertion of cover and article images with proper HTML structure
- **Export Functionality**: Download posts as Markdown files with automatically generated filenames
- **Responsive Interface**: Built with Streamlit for a smooth user experience

## Demo

https://markdown-blog-editor.streamlit.app

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/markdown-blog-editor.git
cd markdown-blog-editor
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the editor:
   - Configure frontmatter in the sidebar
   - Write your content in the Markdown editor
   - See real-time preview on the right
   - Use quick formatting buttons for common elements
   - Export your post when ready

## Frontmatter Structure

The editor generates frontmatter in the following format:

```yaml
---
title: "Your Post Title"
excerpt: "A brief description of your post"
publishDate: '2025-01-09'
tags:
  - Tag1
  - Tag2
seo:
  image:
    src: '/your-image.webp'
    alt: "Image description"
---
```

## Image Templates

### Cover Image
```html
<figure>
  <img id="cover-img" src="/path-to-image.jpg" alt="Image description">
  <figcaption>Photo by <a href="#">Author</a> on <a href="#">Source</a></figcaption>
</figure>
```

### Article Image
```html
<figure>
  <img id="article-img" src="/path-to-image.jpg" alt="Image description">
  <figcaption>"Image caption" \ Source: <a href="#" target="_blank">Source Name</a></figcaption>
</figure>
```

## Development

The application is structured as follows:

- `app.py`: Main application file containing the Streamlit interface
- `requirements.txt`: Python dependencies
- `README.md`: Documentation

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Python-Markdown](https://python-markdown.github.io/)
- YAML handling by [PyYAML](https://pyyaml.org/)
- HTML processing with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
