from weasyprint import HTML, CSS
from flask import current_app
import os

def generate_pdf(html_content):
    """
    Renders HTML content to a PDF using WeasyPrint.
    """
    # Define the path to the compiled CSS
    css_path = os.path.join(current_app.static_folder, 'dist', 'output.css')
    
    # Ensure the CSS file exists (it should be built by Tailwind)
    if not os.path.exists(css_path):
        # Fallback to src/input.css or style.css if dist doesn't exist (dev mode)
        # But for WeasyPrint we really need the full CSS.
        # Let's assume output.css exists or fallback to empty list
        stylesheets = []
    else:
        stylesheets = [CSS(filename=css_path)]

    # Generate PDF
    # base_url is crucial for resolving local images (e.g. /static/images/...)
    # We set it to the static folder or root path
    pdf_bytes = HTML(string=html_content, base_url=current_app.static_folder).write_pdf(
        stylesheets=stylesheets
    )
    
    return pdf_bytes
