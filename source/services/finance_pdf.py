import json
import os
from fpdf import FPDF
from pathlib import Path
from database import queries

# Output directory for the generated PDF reports | Directorio de salida para los reportes PDF generados
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "pdfs"

def generate_finance_pdf(year, lang):
    # Ensure the pdfs folder exists | Asegura que la carpeta pdfs exista
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # --- LOAD LANGUAGE JSON FOR FINANCE PDF | CARGA DEL JSON DE IDIOMA PARA PDF DE FINANZAS ---
    pdf_lang_path = Path(__file__).resolve().parent.parent / "locales" / "languages" / "finances_language" / f"{lang}.json"
    
    try:
        with open(pdf_lang_path, "r", encoding="utf-8") as f:
            t = json.load(f)
    except FileNotFoundError:
        print(f"Error: Language file not found at {pdf_lang_path}")
        return None

    # Fetch data from database using the provided year | Obtiene datos de la DB usando el año provisto
    summary  = queries.get_summary(year)
    income   = queries.get_all_income(year)
    expenses = queries.get_all_expenses(year)
    user     = queries.get_user()

    # PDF Configuration | Configuración del PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- HEADER SECTION | SECCIÓN DE ENCABEZADO ---
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(240, 165, 0) # QuoteCraft Orange
    pdf.cell(0, 10, t["title"].encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"{t['fiscal_year']} {year}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    if user:
        company_text = f"{t['company']} {user['name']}"
        pdf.cell(0, 6, company_text.encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # --- SUMMARY SECTION | SECCIÓN DE RESUMEN ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, t["summary"].encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(2)

    # Financial breakdown | Desglose financiero
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(130, 7, t["total_income"].encode('latin-1', 'replace').decode('latin-1'))
    pdf.set_text_color(34, 201, 122) # Green for income | Verde para ingresos
    pdf.cell(0, 7, f"${summary['total_income']:,.2f}", ln=True)

    pdf.set_text_color(30, 30, 30)
    pdf.cell(130, 7, t["total_expenses"].encode('latin-1', 'replace').decode('latin-1'))
    pdf.set_text_color(255, 95, 109) # Red for expenses | Rojo para gastos
    pdf.cell(0, 7, f"${summary['total_expenses']:,.2f}", ln=True)

    pdf.set_text_color(30, 30, 30)
    pdf.cell(130, 7, t["net_income"].encode('latin-1', 'replace').decode('latin-1'))
    pdf.set_text_color(240, 165, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, f"${summary['net']:,.2f}", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(130, 7, t["deductions"].encode('latin-1', 'replace').decode('latin-1'))
    pdf.cell(0, 7, f"${summary['deductions']:,.2f}", ln=True)

    pdf.ln(4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # --- INCOME TABLE | TABLA DE INGRESOS ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, t["income"].encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(2)

    # Table Header | Encabezado
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(100, 8, t["desc"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True)
    pdf.cell(40,  8, t["date"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True, align="C")
    pdf.cell(40,  8, t["amount"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True, align="R")
    pdf.ln()

    # Rows | Filas
    pdf.set_font("Helvetica", "", 9)
    fill = False
    for i in income:
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 30, 30)
        clean_desc = str(i["description"] or "").encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(100, 7, clean_desc, border=1, fill=fill)
        pdf.cell(40,  7, str(i["date"] or ""),        border=1, fill=fill, align="C")
        pdf.set_text_color(34, 139, 34)
        pdf.cell(40,  7, f"${i['amount']:,.2f}",      border=1, fill=fill, align="R")
        pdf.ln()
        fill = not fill

    pdf.ln(6)

    # --- EXPENSES TABLE | TABLA DE GASTOS ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, t["expenses"].encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(2)

    # Table Header | Encabezado
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(100, 8, t["desc"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True)
    pdf.cell(40,  8, t["date"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True, align="C")
    pdf.cell(40,  8, t["amount"].encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True, align="R")
    pdf.ln()

    # Rows | Filas
    pdf.set_font("Helvetica", "", 9)
    fill = False
    for e in expenses:
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 30, 30)
        clean_desc_e = str(e["description"] or "").encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(100, 7, clean_desc_e, border=1, fill=fill)
        pdf.cell(40,  7, str(e["date"] or ""),        border=1, fill=fill, align="C")
        pdf.set_text_color(180, 0, 0)
        pdf.cell(40,  7, f"${e['amount']:,.2f}",      border=1, fill=fill, align="R")
        pdf.ln()
        fill = not fill

    # --- FOOTER SECTION | SECCIÓN DE PIE DE PÁGINA ---
    pdf.ln(8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, t["footer"].encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
    
    # Save report to path | Guarda el reporte en la ruta
    output_path = OUTPUT_DIR / f"finance_report_{year}.pdf"
    pdf.output(str(output_path))
    return str(output_path)