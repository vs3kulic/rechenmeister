"""This module performs the generation of PDF invoices for the Rechenmeister tool."""
import os
import glob
import logging
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from rich.console import Console

# Initialize the console for rich outputs
console = Console()

def generate_invoice():
    """Handle the generation of the PDF invoice."""
    console.print("🧾 [green]Generate invoice selected.[/green]")

    def get_processed_csv():
        output_folder = "output_csv"
        output_file_pattern = "processed-*.csv"
        output_file_list = glob.glob(os.path.join(output_folder, output_file_pattern))
        if not output_file_list:
            logging.error("No processed CSV file found in 'output_csv' directory.")
            console.print("[bold red]Error:[/bold red] No processed CSV file found in 'output_csv' directory.")
            raise FileNotFoundError("No processed CSV file found in 'output_csv' directory.")
        logging.info("Using processed file: %s", output_file_list[0])
        console.print(f"🧾 [yellow]Using processed file: {output_file_list[0]}...[/yellow]")
        return output_file_list[0]

    def load_dataframe(csv_path):
        dataframe = pd.read_csv(csv_path, delimiter=";")
        if dataframe.empty:
            logging.error("Processed CSV file is empty.")
            console.print("[bold red]Error:[/bold red] Processed CSV file is empty.")
            raise ValueError("Processed CSV file is empty.")
        logging.info("Read processed CSV file into DataFrame.")
        return dataframe

    def build_pdf_table(dataframe):
        columns = ["Datum", "Name", "Stundenbetrag"]
        # Only keep selected columns, fill missing with blank
        df = dataframe.reindex(columns=columns, fill_value="")
        # Keep all rows including summary row
        df = df.replace({pd.NA: "", None: "", float('nan'): "", "nan": ""})
        # Prepare table data
        table_data = [columns]
        for _, row in df.iterrows():
            # For summary row, replace Name with "Summe"
            name_value = "Summe" if row.get("Datum", "").strip() == "Gesamt (Monat)" else row.get("Name", "")
            table_data.append([
                row.get("Datum", ""),
                name_value,
                row.get("Stundenbetrag", "")
            ])
        col_widths = [120, 180, 100]  # px widths for columns
        table = PDFTable(table_data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        return table

    csv_path = get_processed_csv()
    df = load_dataframe(csv_path)
    now = datetime.now()
    pdf_file_name = f"invoice-{now.month:02d}-{now.year}.pdf"
    pdf_dir = "output_pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_file_name)
    logging.info("Creating PDF document: %s", pdf_path)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Add header
    elements = [
        Spacer(1, 6),
        Paragraph(f"Stundenabrechnung {now.month:02d}/{now.year}", styles['Title']),
        Spacer(1, 12)
    ]

    # Add table
    table = build_pdf_table(df)
    elements.append(table)
    elements.append(Spacer(1, 12))

    try:
        doc.build(elements)
        logging.info("PDF invoice generated successfully: %s", pdf_path)
        console.print(f"🧾 [green]PDF invoice generated successfully: {pdf_path}.[/green]")
    except Exception as e:
        logging.error("Failed to generate PDF invoice: %s", e)
        console.print(f"[bold red]Error:[/bold red] Failed to generate PDF invoice: {e}")
        raise IOError(f"Failed to generate PDF invoice: {e}") from e