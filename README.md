# Clipboard2PDF (viewapp.py)

A Streamlit-based web application for creating and viewing PDFs from clipboard content on Windows. This tool allows you to quickly convert rich text, images, and formatted content from your clipboard into PDF documents using Microsoft Word's rendering engine.

## Features

- **📋 Clipboard to PDF**: Convert clipboard content (text, images, formatting) directly to PDF
- **🖥️ Web Interface**: User-friendly Streamlit web application
- **📄 PDF Viewer**: Built-in PDF preview with download capability
- **📝 Content Management**: Append or prepend new content to existing PDFs
- **🎯 Custom Naming**: Set custom filename prefixes for organized file management
- **🔄 Real-time Updates**: Automatic page refresh after PDF creation

## Requirements

### System Requirements
- **Windows** (uses Windows COM interface for Microsoft Word)
- **Microsoft Word** installed and properly configured
- **Python 3.7+**

### Python Dependencies
```
streamlit
pywin32
pypdf (or PyPDF2 as fallback)
```

## Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install streamlit pywin32 pypdf
   ```
   
   Or install from requirements file if available:
   ```bash
   pip install -r requirements-wx.txt
   ```

3. **Verify Microsoft Word** is installed and working on your system

## Usage

### Starting the Application

1. **Navigate** to the project directory:
   ```bash
   cd path/to/richtext2pdf
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run viewapp.py
   ```

3. **Open your browser** to the displayed URL (typically `http://localhost:8501`)

### Creating PDFs

1. Copy content to your clipboard (text, images, formatted content)
2. Enter a filename prefix (optional, defaults to "NotebookLM")
3. Click the "📋 Create PDF" button
4. Your PDF will be created and displayed

### Managing Existing PDFs

When you have an active PDF loaded:

- **Append Mode**: Add new clipboard content to the end of the existing PDF
- **Prepend Mode**: Add new clipboard content to the beginning of the existing PDF
- The mode selector appears automatically when a PDF is loaded

### PDF Output

- PDFs are saved to your system's temporary directory (`%TEMP%`)
- Filename format: `{prefix}_{timestamp}.pdf`
- Example: `NotebookLM_20250606_190145.pdf`

## Key Functions

### `create_pdf(prefix, mode, existing_pdf_path)`
Creates a PDF from clipboard content with options for:
- **prefix**: Custom filename prefix
- **mode**: "new", "append", or "prepend"
- **existing_pdf_path**: Path to existing PDF for append/prepend operations

### `show_pdf(path)`
Displays PDF in the web interface with:
- Embedded PDF viewer
- Download button
- File location information
- Fallback options for browser compatibility

## Technical Details

### Clipboard Processing
- Uses Microsoft Word's COM interface (`win32com.client`)
- Preserves rich formatting, images, and complex layouts
- Handles empty clipboard gracefully with default content
- Proper COM initialization and cleanup

### PDF Management
- Uses `pypdf` (or `PyPDF2`) for PDF merging operations
- Temporary file management for merge operations
- Automatic cleanup of intermediate files

### Web Interface
- Built with Streamlit framework
- Session state management for PDF persistence
- Responsive layout with column-based controls

## Troubleshooting

### Common Issues

**"Microsoft Word not found"**
- Ensure Microsoft Word is properly installed
- Verify Word can be launched normally
- Check Windows COM registration

**"Module not found" errors**
- Install missing dependencies: `pip install streamlit pywin32 pypdf`
- Use virtual environment to avoid conflicts

**PDF not displaying**
- Try the download button as fallback
- Check browser PDF support
- Use the file path to open externally

**Clipboard paste errors**
- Ensure content is copied to clipboard
- Try copying simpler content first
- Check Word's paste capabilities

### Dependencies Installation
```bash
# Primary dependencies
pip install streamlit pywin32

# PDF processing (try pypdf first, fallback to PyPDF2)
pip install pypdf
# OR
pip install PyPDF2
```

## File Structure

```
richtext2pdf/
├── viewapp.py          # Main Streamlit application
├── README.md           # This documentation
├── requirements-wx.txt # Python dependencies
└── ...                 # Other project files
```

## Browser Compatibility

The PDF viewer works best with:
- **Chrome/Edge**: Full PDF display support
- **Firefox**: Good compatibility
- **Safari**: Basic support with download fallback

## License

This project is part of the richtext2pdf toolkit. Check the main project LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on Windows
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all requirements are met
3. Test with simple clipboard content first
4. Create an issue with detailed error information

---

**Note**: This application is specifically designed for Windows systems due to its reliance on Microsoft Word's COM interface. For cross-platform solutions, consider the other tools in this repository.
