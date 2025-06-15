import json
import pandas as pd
import PyPDF2
import re
from datetime import datetime
import argparse

class BiomarkerExtractor:
    def __init__(self):
        self.biomarker_patterns = {
            'Total Cholesterol': r'(?:total\s+)?cholesterol\s*:?\s*(\d+(?:\.\d+)?)',
            'LDL': r'ldl\s*(?:cholesterol)?\s*:?\s*(\d+(?:\.\d+)?)',
            'HDL': r'hdl\s*(?:cholesterol)?\s*:?\s*(\d+(?:\.\d+)?)',
            'Triglycerides': r'triglycerides?\s*:?\s*(\d+(?:\.\d+)?)',
            'Creatinine': r'creatinine\s*:?\s*(\d+(?:\.\d+)?)',
            'Vitamin D': r'vitamin\s+d\s*(?:25\s*oh)?\s*:?\s*(\d+(?:\.\d+)?)',
            'Vitamin B12': r'(?:vitamin\s+)?b\s*12\s*:?\s*(\d+(?:\.\d+)?)',
            'HbA1c': r'hba1c\s*:?\s*(\d+(?:\.\d+)?)',
        }
    
    def extract_from_pdf(self, pdf_path):
        """Extract biomarker data from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                return self.parse_text_for_biomarkers(text)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return {}
    
    def parse_text_for_biomarkers(self, text):
        """Parse text and extract biomarker values"""
        text = text.lower()
        extracted_data = {}
        
        # Extract date from text
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        report_date = datetime.now().strftime('%Y-%m-%d')
        if date_match:
            try:
                report_date = datetime.strptime(date_match.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')
            except:
                pass
        
        # Extract biomarker values
        for biomarker, pattern in self.biomarker_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = float(matches[0])
                extracted_data[biomarker] = [{
                    'date': report_date,
                    'value': value
                }]
        
        return extracted_data
    
    def extract_from_csv(self, csv_path):
        """Extract biomarker data from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            extracted_data = {}
            
            for column in df.columns:
                if column.lower() in ['date', 'time', 'timestamp']:
                    continue
                    
                # Check if column name matches any biomarker
                for biomarker in self.biomarker_patterns.keys():
                    if biomarker.lower() in column.lower():
                        data_points = []
                        for _, row in df.iterrows():
                            if pd.notna(row[column]):
                                date = row.get('date', row.get('Date', datetime.now().strftime('%Y-%m-%d')))
                                data_points.append({
                                    'date': str(date),
                                    'value': float(row[column])
                                })
                        extracted_data[biomarker] = data_points
                        break
            
            return extracted_data
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return {}
    
    def save_to_json(self, data, output_path):
        """Save extracted data to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data saved to {output_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract biomarker data from health reports')
    parser.add_argument('input_file', help='Input file path (PDF or CSV)')
    parser.add_argument('--output', '-o', default='extracted_data.json', help='Output JSON file path')
    
    args = parser.parse_args()
    
    extractor = BiomarkerExtractor()
    
    if args.input_file.lower().endswith('.pdf'):
        data = extractor.extract_from_pdf(args.input_file)
    elif args.input_file.lower().endswith('.csv'):
        data = extractor.extract_from_csv(args.input_file)
    else:
        print("Unsupported file format. Please use PDF or CSV files.")
        return
    
    if data:
        extractor.save_to_json(data, args.output)
        print(f"Extracted data for {len(data)} biomarkers")
    else:
        print("No biomarker data found in the file")

if __name__ == "__main__":
    main()