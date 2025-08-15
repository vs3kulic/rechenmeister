
# Rechenmeister - Invoice Automation

## Overview

Automated invoice generation system for partners based on a class-based flat rate billing model with bonus incentives.


## Billing Model Features

### Class-Based Flat Rate System
- Each class is identified by its name
- Each class is assigned a fixed flat rate (hourly rate)
- Default hourly rate: €20 per hour
- Hourly rates can vary per class type

### Calculation Logic
- Registration Rate: `Registered / Max Participants * 100`
- Duration: Calculated from `End Time - Start Time`
- Base Payment: `Duration * Hourly Rate`
- Final Payment: `Base Payment * Bonus Multiplier`

### Bonus Incentive System
- +50% bonus: Minimum 50% registration rate
- +100% bonus: 100% registration rate


## Monthly Processing Workflow

Each month, a new CSV file is stored in the `input_csv/` directory and extended with calculated columns.

### Class Status Filtering
Only classes with specific statuses are included in billing:
- Bookable/active classes
- Cancelled classes are excluded

### New Columns Added
1. Duration - Class duration in hours
2. Hourly Rate - Base hourly rate
3. Registration Rate - Registration percentage
4. Bonus Factor - Bonus multiplier based on registration rate
5. Final Hourly Rate - Hourly rate including bonus
6. Total Payment - Total payment for the class


## Implementation

- Python-based command-line utility for automated invoice processing.
- Supports four main operations via interactive CLI menu:
  - File Ingestion: Move and rename source CSV to input_csv.
  - Data Processing: Filter, compute billing columns, output to output_csv.
  - PDF Generation: Render invoice data from CSV to PDF and save to output_pdf.
  - Log Inspection: View operation logs for auditing and troubleshooting.
- Modular codebase: CSV I/O, data transformation, PDF rendering, and logging are separated into distinct components.