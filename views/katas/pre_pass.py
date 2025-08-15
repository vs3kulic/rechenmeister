"""This is the pre-pass for the Rechenmeister project."""

#-------------------
# INPUT
#-------------------
# The source file contains data about yoga classes and is expected to be in the Downloads folder
# The file name is "Aktivitätsbericht von Alle Aktivitätstypen YYYY-MM-DD-YYYY-MM-DD", the file extension is .csv
# The file should be moved to the input_csv/ directory and re-named to "aktivitaetsbericht-MM-YYYY.csv"

#-------------------
# VALIDATION
#-------------------
# The input file must be a valid CSV file
# The input file must contain the following columns:
# - class_name: Name of the yoga class
# - class_date: Date of the yoga class
# - teacher_name: Name of the yoga teacher

#--------------------
# PROCESSING
#--------------------
# Add new columns to the CSV file:
# - Class duration in hours (Dauer, calculated: Endzeit - Startzeit)
# - Base hourly rate (Stundensatz, default: €20)
# - Registration percentage (Anmeldequote, calculated: Angemeldet / Max. Teilnehmer * 100)
# - Bonus multiplier based on registration rate (Bonus-Faktor):
#   - 1.0 for <50% registration
#   - 1.5 for 50-99% registration
#   - 2.0 for 100% registration
# Final hourly rate including bonus (Stundensatz_Final, calculated: Stundensatz * Bonus_Faktor)
# Total payment for the class (Gesamt_Vergütung, calculated: Dauer * Stundensatz_Final)

# Filter classes based on their status:
# Only classes with specific statuses are included in billing:
# - buchbar - Bookable/active classes
# - Classes with Storniert status are excluded from billing

#--------------------
# OUTPUT
#--------------------
# The processed CSV file is saved to the output_csv/ directory
