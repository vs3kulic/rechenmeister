# Rechenmeister - be kind Yoga Studio Partner Invoice Automation

## Overview

Automated invoice generation system for yoga studio partners based on a class-based flat rate billing model with bonus incentives.

## Billing Model Features

### Class-Based Flat Rate System
- Each yoga class is individually identified by its name
- Each class is assigned a fixed flat rate (hourly rate)
- **Default hourly rate**: €20 per hour
- Future flexibility: hourly rates can vary per class type

### Calculation Logic
- **Registration Rate (Anmeldequote)**: `Angemeldet / Max. Teilnehmer * 100`
- **Duration**: Calculated from `Endzeit - Startzeit`
- **Base Payment**: `Duration * Stundensatz`
- **Final Payment**: `Base Payment * Bonus Multiplier`

### Bonus Incentive System
The bonus system aims to reward high class utilization while protecting trainers from short-term participant cancellations:

- **+50% bonus**: Minimum 50% registration rate (Anmeldequote)
- **+100% bonus**: 100% registration rate
- **Example**: 
  - Base rate €20, 100% registration → €40 per hour
  - Base rate €20, 50-99% registration → €30 per hour
  - Base rate €20, <50% registration → €20 per hour

## Monthly Processing Workflow

Each month, a new CSV file is stored in the `input_csv/` directory and extended with calculated columns:

### Class Status Filtering
Only classes with specific statuses are included in billing:
- `buchbar` - Bookable/active classes
- Classes with `Storniert` status are excluded from billing

### New Columns Added
1. **Dauer** - Class duration in hours (calculated: `Endzeit - Startzeit`)
2. **Stundensatz** - Base hourly rate (default: €20)
3. **Anmeldequote** - Registration percentage (`Angemeldet / Max. Teilnehmer * 100`)
4. **Bonus_Faktor** - Bonus multiplier based on registration rate:
   - `1.0` for <50% registration
   - `1.5` for 50-99% registration  
   - `2.0` for 100% registration
5. **Stundensatz_Final** - Final hourly rate including bonus (`Stundensatz * Bonus_Faktor`)
6. **Gesamt_Vergütung** - Total payment for the class (`Dauer * Stundensatz_Final`)

## Implementation

- Python-based command-line utility for automated invoice processing.
- Supports four main operations, selectable via interactive CLI menu:
  - File Ingestion: Move and rename source CSV from Downloads to input_csv as activities-MM-YYYY.csv.
  - Data Processing: Filter by teacher name and class status, compute billing columns, output to output_csv/invoice-{teacher}-MM-YYYY.csv.
  - PDF Generation: Render invoice data from CSV to PDF with structured header, main table, and footer; save to output_pdf.
  - Log Inspection: View operation logs for auditing and troubleshooting. All operations are logged for traceability.
- Modular codebase: CSV I/O, data transformation, PDF rendering, and logging are separated into distinct components.