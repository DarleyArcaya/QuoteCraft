import json
from fpdf import FPDF
from pathlib import Path
from database import queries

# Define output directory for PDFs | Define el directorio de salida para los PDFs
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "pdfs"
# Base path for PDF translation files | Ruta base para los archivos de traducción del PDF
LOCALES_PATH_BASE = Path(__file__).resolve().parent.parent / "locales" / "pdf" / "estimates_language"

def generate_pdf(estimate_id, lang=None):
    # Create the output directory if it doesn't exist | Crea el directorio de salida si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get data from database | Obtiene los datos de la base de datos
    estimate = queries.get_estimate(estimate_id)
    items    = queries.get_items(estimate_id)

    if not estimate:
        return None

    # --- LANGUAGE LOGIC | LÓGICA DE IDIOMA ---
    # Use provided language or fallback to estimate's saved language | Usa el idioma provisto o el guardado en el estimado
    if lang is None:
        lang = estimate.get("language", "es")
    
    if not lang:
        lang = "es"

    # Dynamic loading of the translation file | Carga dinámica del archivo de traducción
    json_file = LOCALES_PATH_BASE / f"{lang}.json"
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            tr = json.load(f)
    except Exception:
        # Safety fallback if file is missing | Fallback de seguridad si falta el archivo
        tr = {"title": "ESTIMADO"} if lang == "es" else {"title": "ESTIMATE"}

    # Map categories for translation | Mapa de categorías para traducción
    categories_map = tr.get("categories", {})

    # PDF Initialization | Inicialización del PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- HEADER SECTION | SECCIÓN DE ENCABEZADO ---
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(240, 165, 0) # QuoteCraft Orange | Naranja QuoteCraft
    pdf.cell(0, 10, tr.get("title", "ESTIMADO").encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"{tr.get('number', 'Numero')}: {estimate['estimate_number']}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 6, f"{tr.get('date', 'Fecha')}: {estimate['created_at']}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 6, f"{tr.get('valid', 'Valido hasta')}: {estimate['valid_until'] or 'N/A'}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(6)
    pdf.set_draw_color(40, 40, 40)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y()) # Horizontal line | Línea horizontal
    pdf.ln(6)

    # --- COMPANY INFO | INFO DE LA EMPRESA ---
    user = queries.get_user()
    if user:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(240, 165, 0)
        pdf.cell(0, 6, tr.get("company", "EMPRESA").encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 6, (user["name"] or "").encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        if user["phone"]:
            pdf.cell(0, 5, f"Tel: {user['phone']}", ln=True)
        if user["email"]:
            pdf.cell(0, 5, f"Email: {user['email']}", ln=True)
        if user["address"]:
            pdf.cell(0, 5, user["address"].encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.ln(4)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(6)

    # --- CLIENT INFO | INFO DEL CLIENTE ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, tr.get("client", "CLIENTE").encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 6, f"{tr.get('name', 'Nombre')}:    {estimate['client_name']}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 6, f"{tr.get('phone', 'Telefono')}:  {estimate['client_phone'] or 'N/A'}", ln=True)
    pdf.cell(0, 6, f"Email:     {estimate['client_email'] or 'N/A'}", ln=True)
    pdf.cell(0, 6, f"{tr.get('address', 'Direccion')}: {estimate['client_address'] or 'N/A'}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # --- PROJECT DESCRIPTION | DESCRIPCIÓN DEL PROYECTO ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, tr.get("project", "PROYECTO").encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    desc_text = estimate['description'] or tr.get('no_desc', 'Sin descripcion')
    pdf.cell(0, 6, desc_text.encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # --- ITEMS TABLE | TABLA DE ARTÍCULOS ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(0, 6, tr.get("work_lines", "LINEAS DE TRABAJO").encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(2)

    # Table Header | Encabezado de la tabla
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(45, 8, tr.get("col_cat", "Categoria").encode('latin-1', 'replace').decode('latin-1'),  border=1, fill=True)
    pdf.cell(75, 8, tr.get("col_desc", "Descripcion").encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True)
    pdf.cell(15, 8, tr.get("col_qty", "Cant.").encode('latin-1', 'replace').decode('latin-1'),  border=1, fill=True, align="C")
    pdf.cell(20, 8, tr.get("col_unit", "Unidad").encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True, align="C")
    pdf.cell(25, 8, tr.get("col_sub", "Subtotal").encode('latin-1', 'replace').decode('latin-1'),  border=1, fill=True, align="R")
    pdf.ln()

    # Table Rows | Filas de la tabla
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    fill = False
    for item in items:
        raw_cat = str(item["category"] or "")
        translated_cat = categories_map.get(raw_cat, raw_cat)

        subtotal_item = (item["quantity"] or 0) * (item["unit_price"] or 0)
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        
        clean_cat = translated_cat.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(45, 7, clean_cat,   border=1, fill=fill)
        pdf.cell(75, 7, str(item["description"] or "").encode('latin-1', 'replace').decode('latin-1'), border=1, fill=fill)
        pdf.cell(15, 7, str(item["quantity"] or ""),    border=1, fill=fill, align="C")
        pdf.cell(20, 7, str(item["unit"] or "").encode('latin-1', 'replace').decode('latin-1'),         border=1, fill=fill, align="C")
        pdf.cell(25, 7, f"${subtotal_item:,.2f}",             border=1, fill=fill, align="R")
        pdf.ln()
        fill = not fill

    pdf.ln(4)

    # --- TOTALS | TOTALES ---
    tax_amount = (estimate["subtotal"] or 0) * (estimate["tax_rate"] or 0)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(155, 7, f"{tr.get('subtotal', 'Subtotal')}:".encode('latin-1', 'replace').decode('latin-1'), align="R")
    pdf.cell(25, 7, f"${estimate['subtotal']:,.2f}", align="R", ln=True)

    tax_label = tr.get('tax', 'Impuesto')
    pdf.cell(155, 7, f"{tax_label} ({(estimate['tax_rate'] or 0)*100:.1f}%):".encode('latin-1', 'replace').decode('latin-1'), align="R")
    pdf.cell(25, 7, f"${tax_amount:,.2f}", align="R", ln=True)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(240, 165, 0)
    pdf.cell(155, 8, "TOTAL:", align="R")
    pdf.cell(25, 8, f"${estimate['total']:,.2f}", align="R", ln=True)

    pdf.ln(6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # --- NOTES & TERMS | NOTAS Y CONDICIONES ---
    if estimate["notes"]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(240, 165, 0)
        pdf.cell(0, 6, tr.get("notes", "NOTAS Y CONDICIONES").encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        notes_clean = estimate["notes"].encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, notes_clean)

    # --- FOOTER | PIE DE PÁGINA ---
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(180, 180, 180)
    footer_text = tr.get("footer", "Generado con QuoteCraft")
    pdf.cell(0, 5, footer_text.encode('latin-1', 'replace').decode('latin-1'), align="C")

    # Save the file | Guarda el archivo
    output_path = OUTPUT_DIR / f"{estimate['estimate_number']}.pdf"
    pdf.output(str(output_path))
    return str(output_path)