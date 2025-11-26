from playwright.sync_api import sync_playwright

def generate_pdf(html_content):
    """
    Renders HTML content to a PDF using a headless browser.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Set content
        page.set_content(html_content)
        
        # Wait for images to load
        page.wait_for_load_state("networkidle")
        
        # Generate PDF (A4 size)
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )
        browser.close()
        return pdf_bytes
