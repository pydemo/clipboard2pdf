from os.path import isfile
import streamlit as st, base64, pathlib, os

def create_pdf(prefix="clipboard", mode="new", existing_pdf_path=None):
    import os, tempfile, datetime, win32com.client, pythoncom  # pip install pywin32

    # Initialize COM
    pythoncom.CoInitialize()
    
    try:
        wdFormatPDF = 17                       # constant for PDF export
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False                   # keep UI hidden
        
        if mode == "new" or not existing_pdf_path or not os.path.exists(existing_pdf_path):
            # Create new PDF
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.pdf"
            outfile = os.path.join(tempfile.gettempdir(), filename)
            
            doc = word.Documents.Add()           # blank document
            
            # Check if clipboard has content
            try:
                doc.Content.Paste()                  # paste *as Word sees it* (text + pictures)
                content_length = len(doc.Content.Text)
                print(f"Content pasted, length: {content_length}")
                
                if content_length <= 1:  # Empty or just paragraph mark
                    # Add some default text if clipboard is empty
                    doc.Content.Text = "No content found in clipboard. This is a test PDF."
                    
            except Exception as paste_error:
                print(f"Paste error: {paste_error}")
                # Add default text if paste fails
                doc.Content.Text = "Failed to paste clipboard content. This is a test PDF."
            
            doc.ExportAsFixedFormat(outfile, wdFormatPDF)
            doc.Close(False)
            
        else:
            # For append/prepend modes, create a new merged PDF with unique name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{mode}_{timestamp}.pdf"
            outfile = os.path.join(tempfile.gettempdir(), filename)
            
            # Create temporary PDF with new clipboard content
            temp_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_clipboard_{temp_timestamp}.pdf"
            temp_pdf_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            # Create new document with clipboard content
            doc = word.Documents.Add()
            try:
                doc.Content.Paste()
                content_length = len(doc.Content.Text)
                print(f"New content pasted, length: {content_length}")
                
                if content_length <= 1:  # Empty or just paragraph mark
                    doc.Content.Text = "No new content found in clipboard."
                    
            except Exception as paste_error:
                print(f"Paste error: {paste_error}")
                doc.Content.Text = "Failed to paste new clipboard content."
            
            doc.ExportAsFixedFormat(temp_pdf_path, wdFormatPDF)
            doc.Close(False)
            
            # Verify temporary PDF was created
            if not os.path.exists(temp_pdf_path) or os.path.getsize(temp_pdf_path) == 0:
                raise Exception("Failed to create temporary PDF with new content")
            
            # Now merge the PDFs using pypdf
            try:
                from pypdf import PdfReader, PdfWriter
            except ImportError:
                try:
                    from PyPDF2 import PdfReader, PdfWriter
                except ImportError:
                    raise ImportError("Please install pypdf or PyPDF2: pip install pypdf")
            
            # Validate existing PDF
            if not os.path.exists(existing_pdf_path) or os.path.getsize(existing_pdf_path) == 0:
                raise Exception("Existing PDF file is invalid or empty")
            
            # Create merged PDF
            writer = PdfWriter()
            
            try:
                if mode == "prepend":
                    # Add new content first, then existing content
                    print("Adding new content first (prepend mode)")
                    new_reader = PdfReader(temp_pdf_path)
                    for i, page in enumerate(new_reader.pages):
                        writer.add_page(page)
                        print(f"Added new page {i+1}")
                    
                    print("Adding existing content")
                    existing_reader = PdfReader(existing_pdf_path)
                    for i, page in enumerate(existing_reader.pages):
                        writer.add_page(page)
                        print(f"Added existing page {i+1}")
                else:  # append
                    # Add existing content first, then new content
                    print("Adding existing content first (append mode)")
                    existing_reader = PdfReader(existing_pdf_path)
                    for i, page in enumerate(existing_reader.pages):
                        writer.add_page(page)
                        print(f"Added existing page {i+1}")
                    
                    print("Adding new content")
                    new_reader = PdfReader(temp_pdf_path)
                    for i, page in enumerate(new_reader.pages):
                        writer.add_page(page)
                        print(f"Added new page {i+1}")
                
                # Save merged PDF
                with open(outfile, 'wb') as output_file:
                    writer.write(output_file)
                
                # Verify merged PDF was created successfully
                if not os.path.exists(outfile) or os.path.getsize(outfile) == 0:
                    raise Exception("Failed to create merged PDF")
                
                print(f"Merged PDF created successfully: {outfile}")
                
            except Exception as merge_error:
                print(f"PDF merge error: {merge_error}")
                raise Exception(f"Failed to merge PDFs: {merge_error}")
            
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)
                        print("Temporary PDF cleaned up")
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file: {cleanup_error}")
        
        word.Quit()
        print("Saved:", outfile)
        return outfile
        
    except Exception as e:
        # Ensure Word is closed even if there's an error
        try:
            word.Quit()
        except:
            pass
        print(f"Error in create_pdf: {e}")
        raise e
    finally:
        # Clean up COM
        pythoncom.CoUninitialize()


def show_pdf(path: str | pathlib.Path):
    """Display PDF using streamlit's built-in capabilities with fallback options"""
    try:
        # Validate the PDF file
        if not os.path.exists(path):
            st.error(f"PDF file not found: {path}")
            return
        
        file_size = os.path.getsize(path)
        if file_size == 0:
            st.error("PDF file is empty")
            return
        
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        
        # Validate PDF content
        if len(pdf_bytes) == 0:
            st.error("PDF file contains no data")
            return
        
        # Extract filename from path
        filename = os.path.basename(path)
        
        # Method 1: Download button (always works)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            key=f"download_{filename}"
        )
        
        st.markdown("### PDF Preview")
        
        # Method 2: Use a simplified approach - just show the first few KB as text preview
        # and provide links to open externally
        try:
            # Check if it's a valid PDF by looking at the header
            pdf_header = pdf_bytes[:10]
            if pdf_header.startswith(b'%PDF-'):
                st.success("✅ Valid PDF file detected")
                
                # Try to extract text from first page for preview
                try:
                    from pypdf import PdfReader
                    import io
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    if len(reader.pages) > 0:
                        first_page_text = reader.pages[0].extract_text()
                        if first_page_text.strip():
                            st.markdown("**Text Content Preview (First Page):**")
                            # Show first 500 characters
                            preview_text = first_page_text[:500]
                            if len(first_page_text) > 500:
                                preview_text += "..."
                            st.text(preview_text)
                        else:
                            st.info("PDF contains no extractable text (may be image-based)")
                    else:
                        st.warning("PDF appears to have no pages")
                except Exception as text_error:
                    st.warning(f"Could not extract text preview: {text_error}")
                
                # Create buttons to open PDF externally
                st.markdown("**Open PDF:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Open with Default", key="open_default"):
                        try:
                            # Use os.startfile to open with default application
                            os.startfile(str(path))
                            st.success("PDF opened with default application")
                        except Exception as e:
                            st.error(f"Could not open PDF: {e}")
                
                with col2:
                    if st.button("🌐 Force Browser", key="open_browser"):
                        try:
                            import webbrowser
                            import tempfile
                            import shutil
                            import urllib.parse
                            
                            # Copy to a temp file with .pdf extension for browser access
                            temp_dir = tempfile.gettempdir()
                            safe_filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
                            temp_pdf = os.path.join(temp_dir, f"browser_{safe_filename}")
                            
                            # Copy the file
                            shutil.copy2(path, temp_pdf)
                            st.info(f"Copied PDF to: {temp_pdf}")
                            
                            # Create proper file URL
                            temp_pdf_escaped = temp_pdf.replace('\\', '/')
                            file_url = f"file:///{temp_pdf_escaped}"
                            
                            # Make the URL clickable in new tab
                            st.markdown(f"**Opening URL:** <a href='{file_url}' target='_blank'>Click here to open PDF</a>", unsafe_allow_html=True)
                            st.code(file_url)
                            
                            # Try to open in browser
                            opened = False
                            
                            # Method 1: Try default browser first
                            try:
                                webbrowser.open(file_url, new=2)  # new=2 opens in new tab
                                st.success("PDF opened in default browser")
                                opened = True
                            except Exception as e1:
                                st.warning(f"Default browser failed: {e1}")
                            
                            # Method 2: Try Chrome specifically
                            if not opened:
                                try:
                                    chrome = webbrowser.get('chrome')
                                    chrome.open(file_url, new=2)
                                    st.success("PDF opened in Chrome")
                                    opened = True
                                except Exception as e2:
                                    st.warning(f"Chrome failed: {e2}")
                            
                            # Method 3: Try Edge specifically  
                            if not opened:
                                try:
                                    edge = webbrowser.get('edge')
                                    edge.open(file_url, new=2)
                                    st.success("PDF opened in Edge")
                                    opened = True
                                except Exception as e3:
                                    st.warning(f"Edge failed: {e3}")
                            
                            # Method 4: Try system default
                            if not opened:
                                try:
                                    os.startfile(temp_pdf)
                                    st.success("PDF opened with system default")
                                    opened = True
                                except Exception as e4:
                                    st.warning(f"System default failed: {e4}")
                            
                            if not opened:
                                st.error("Could not open PDF in any browser")
                                st.code(f"Manual file path: {temp_pdf}")
                                    
                        except Exception as e:
                            st.error(f"Error in browser opening: {str(e)}")
                            st.code(f"Original file path: {str(path)}")
                
                with col3:
                    if st.button("📂 File Location", key="open_location"):
                        try:
                            import subprocess
                            
                            # Use different methods depending on OS
                            if os.name == 'nt':  # Windows
                                # Simplified approach - use only one method to avoid multiple windows
                                try:
                                    # Method 1: Try subprocess with full explorer path
                                    explorer_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'explorer.exe')
                                    subprocess.run([explorer_path, '/select,', str(path)], check=True)
                                    st.success("File location opened in Explorer")
                                except (subprocess.CalledProcessError, FileNotFoundError):
                                    try:
                                        # Method 2: Fallback to os.startfile for folder only
                                        folder_path = os.path.dirname(path)
                                        os.startfile(folder_path)
                                        st.success("Folder opened in Explorer")
                                    except Exception:
                                        # Method 3: Show manual path as last resort
                                        st.warning("Could not open file location automatically")
                                        st.code(f"Manual path: {str(path)}")
                                        
                            else:
                                # For non-Windows systems
                                try:
                                    folder_path = os.path.dirname(path)
                                    os.startfile(folder_path)
                                    st.success("Folder opened")
                                except Exception as e:
                                    st.error(f"Could not open folder: {e}")
                                    st.code(f"Manual path: {str(path)}")
                                
                        except Exception as e:
                            st.error(f"Could not open file location: {e}")
                            st.code(f"Manual path: {str(path)}")
                
                # Show file path for manual access
                st.markdown("**Manual Access:**")
                st.code(str(path))
                st.info("💡 You can copy the path above and paste it into your file explorer or Clipboard-to-PDF")
                
            else:
                st.error("File does not appear to be a valid PDF")
                
        except Exception as display_error:
            st.error(f"Failed to process PDF: {display_error}")
        
        # Method 3: Show file information and location
        st.markdown("### File Information")
        st.text(f"File: {filename}")
        st.text(f"Location: {path}")
        st.text(f"Size: {file_size:,} bytes")
        
        # Try to extract basic PDF info
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            st.text(f"Pages: {len(reader.pages)}")
            if reader.metadata:
                if '/Title' in reader.metadata:
                    st.text(f"Title: {reader.metadata['/Title']}")
                if '/Author' in reader.metadata:
                    st.text(f"Author: {reader.metadata['/Author']}")
        except Exception as info_error:
            st.text(f"Could not extract PDF info: {info_error}")
            
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")
        st.text(f"File path: {path}")
        if os.path.exists(path):
            st.text(f"File exists but cannot be read")
        else:
            st.text(f"File does not exist")

# Main application logic
st.title("Clipboard-to-PDF")

# Initialize session state
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None

# JavaScript for keyboard shortcut detection
keyboard_js = """
<script>
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'v') {
        event.preventDefault();
        
        // Add query parameter and reload page
        const url = new URL(window.location);
        url.searchParams.set('ctrl_v', 'true');
        window.location.href = url.toString();
    }
});
</script>
"""

st.markdown(keyboard_js, unsafe_allow_html=True)

# Check if Ctrl+V was pressed (using query params)
query_params = st.query_params
ctrl_v_triggered = 'ctrl_v' in query_params and query_params['ctrl_v'] == 'true'

if ctrl_v_triggered:
    # Clear the query parameter to avoid retriggering
    st.query_params.clear()

# Create columns for controls
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    # Text input for PDF filename prefix
    pdf_prefix = st.text_input(
        "PDF filename prefix:",
        value="NotebookLM",
        placeholder="Enter filename prefix",
        help="The PDF will be saved as: prefix_timestamp.pdf"
    )

with col2:
    # Radio buttons for append/prepend mode (only show if PDF exists)
    if st.session_state.pdf_path and isfile(st.session_state.pdf_path):
        pdf_mode = st.radio(
            "Content mode:",
            options=["append", "prepend"],
            index=0,
            help="Append: Add new content to end\nPrepend: Add new content to beginning"
        )
    else:
        pdf_mode = "new"
        st.write("")  # Empty space when no PDF exists

with col3:
    # Add some spacing to align button with text input
    st.write("")  # Empty line for spacing
    # Button to create PDF from clipboard (also triggered by Ctrl+V)
    if st.session_state.pdf_path and isfile(st.session_state.pdf_path):
        button_text = "📋 Add to PDF (Ctrl+V)"
    else:
        button_text = "📋 Create PDF (Ctrl+V)"
    
    create_pdf_clicked = st.button(button_text, key="create_pdf_btn")

with col4:
    # Add some spacing to align button with text input
    st.write("")  # Empty line for spacing
    # Reset button - only show if there's a PDF loaded
    if st.session_state.pdf_path and isfile(st.session_state.pdf_path):
        reset_clicked = st.button("🔄 Reset", key="reset_btn", help="Clear PDF and cache, keep filename prefix")
    else:
        reset_clicked = False
        st.write("")  # Empty space when no PDF exists

# Handle reset button click
if reset_clicked:
    # Clear PDF path from session state
    st.session_state.pdf_path = None
    
    # Clear any query parameters that might be cached
    st.query_params.clear()
    
    # Show success message
    st.success("🔄 Reset complete! PDF cleared, cache cleared. Filename prefix preserved.")
    st.rerun()

if create_pdf_clicked or ctrl_v_triggered:
    # Use the prefix from the text input, or default if empty
    prefix = pdf_prefix.strip() if pdf_prefix.strip() else "document"
    
    # Determine the mode and existing PDF path
    existing_pdf = st.session_state.pdf_path if st.session_state.pdf_path and isfile(st.session_state.pdf_path) else None
    mode = pdf_mode if existing_pdf else "new"
    
    try:
        with st.spinner(f"{'Adding content to' if existing_pdf else 'Creating'} PDF from clipboard..."):
            pdf_path = create_pdf(prefix, mode, existing_pdf)
            st.session_state.pdf_path = pdf_path
        
        if existing_pdf:
            st.success(f"Content {'appended to' if mode == 'append' else 'prepended to'} PDF: {os.path.basename(pdf_path)}")
        else:
            st.success(f"PDF created successfully: {os.path.basename(pdf_path)}")
        st.rerun()
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")

# Display PDF if one exists
if st.session_state.pdf_path and isfile(st.session_state.pdf_path):
    # Debug information
    file_size = os.path.getsize(st.session_state.pdf_path)
    st.info(f"📄 PDF loaded: {os.path.basename(st.session_state.pdf_path)} ({file_size:,} bytes)")
    
    if file_size > 0:
        show_pdf(st.session_state.pdf_path)
    else:
        st.error("PDF file is empty. Please try creating the PDF again.")
else:
    # Show empty Clipboard-to-PDF
    st.markdown("### PDF Preview")
    st.info("📄 No PDF loaded. Press **Ctrl+V** or click the button above to create a PDF from your clipboard content.")
    
    # Empty Clipboard-to-PDF placeholder
    empty_viewer = '''
    <div style="border: 2px dashed #ccc; height: 400px; display: flex; align-items: center; justify-content: center; background-color: #f9f9f9;">
        <div style="text-align: center; color: #666;">
            <h3>Clipboard-to-PDF</h3>
            <p>Your PDF will appear here</p>
        </div>
    </div>
    '''
    st.markdown(empty_viewer, unsafe_allow_html=True)
