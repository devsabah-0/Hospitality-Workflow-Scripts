import os
import pdfplumber
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Suppress the Tkinter deprecation warning on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_country_data(text):
    # Regex pattern to match each line of country data
    pattern = re.compile(
        r"^([\w\s()'-]+)\s+"  # Country name
        r"(\d+)\s+"           # Arrivals
        r"(\d+)\s+"           # Stay Per
        r"([\d,]+\.\d{2})\s+" # Room Rev
        r"([\d,]+\.\d{2})\s+" # Total Rev
        r"(\d+)\s+"           # Room Nts
        r"([\d,]+\.\d{2})\s+" # ADR
        r"([\d.]+)%$",        # OCC%
        re.MULTILINE
    )

    # Find all matches and extract the data
    matches = pattern.findall(text)

    country_data = []
    for match in matches:
        country_name = match[0].strip()
        arrivals = int(match[1])
        stay_per = int(match[2])
        room_rev = float(match[3].replace(',', ''))
        total_rev = float(match[4].replace(',', ''))
        room_nts = int(match[5])
        adr = float(match[6].replace(',', ''))
        occ = float(match[7])

        country_data.append({
            "Country": country_name,
            "Arrivals": arrivals,
            "Stay Per": stay_per,
            "Room Rev": room_rev,
            "Total Rev": total_rev,
            "Room Nts": room_nts,
            "ADR": adr,
            "OCC%": occ
        })

    return country_data

def calculate_stay_percentage(country_data):
    total_stay = sum(country["Stay Per"] for country in country_data)
    for country in country_data:
        country["Stay Percentage"] = (country["Stay Per"] / total_stay) * 100 if total_stay > 0 else 0
    return country_data

def main():
    # Use Tkinter to open a file dialog and select the PDF file
    Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
    file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
    
    if not file_path:
        print("No file selected.")
        return

    text = extract_text_from_pdf(file_path)
    country_data = parse_country_data(text)

    if not country_data:
        print("No country data found. Check the regex pattern and extracted text.")
    else:
        country_data = calculate_stay_percentage(country_data)
        top_countries = sorted(country_data, key=lambda x: x["Stay Percentage"], reverse=True)[:10]

        print("\nTop 10 Countries by Stay Percentage:")
        for country_info in top_countries:
            print(f"{country_info['Country']}: {country_info['Stay Percentage']:.2f}%")

if __name__ == "__main__":
    main()
