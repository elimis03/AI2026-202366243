import os
import sys
from docx2pdf import convert

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

workspace_dir = r"c:\Users\user\Desktop\test folder"
docx_path = os.path.join(workspace_dir, "자살률_삶만족도_상관관계_분석보고서.docx")
pdf_path = os.path.join(workspace_dir, "자살률_삶만족도_상관관계_분석보고서.pdf")

print("Starting docx to pdf conversion...")
try:
    convert(docx_path, pdf_path)
    print(f"Success! PDF created at: {pdf_path}")
except Exception as e:
    print(f"Error during docx2pdf conversion: {e}")
    sys.exit(1)
