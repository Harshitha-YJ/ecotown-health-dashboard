#!/usr/bin/env python3
"""
PDF Parser for EcoTown Health Dashboard
Advanced PDF parsing with OCR support for extracting biomarker data from health reports
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

# Core PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Install with: pip install PyPDF2 pdfplumber pdf2image pytesseract pillow pandas numpy")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedPDFParser:
    """Advanced PDF parser with multiple extraction methods and OCR support"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize parser with configuration"""
        self.biomarker_patterns = self._load_biomarker_patterns()
        self.date_patterns = self._load_date_patterns()
        self.unit_conversions = self._load_unit_conversions()
        self.clinical_ranges = self._load_clinical_ranges()
        
        # OCR configuration
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:/-() '
        
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)
    
    def _load_biomarker_patterns(self) -> Dict[str, List[str]]:
        """Load comprehensive biomarker extraction patterns"""
        return {
            'Total Cholesterol': [
                r'(?:total\s+)?cholesterol\s*:?\s*(\d+(?:\.\d+)?)',
                r'cholesterol,?\s*total\s*:?\s*(\d+(?:\.\d+)?)',
                r'chol\s*:?\s*(\d+(?:\.\d+)?)',
                r'tc\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'LDL': [
                r'ldl\s*(?:cholesterol)?\s*:?\s*(\d+(?:\.\d+)?)',
                r'low\s*density\s*lipoprotein\s*:?\s*(\d+(?:\.\d+)?)',
                r'ldl-c\s*:?\s*(\d+(?:\.\d+)?)',
                r'cholesterol,?\s*ldl\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'HDL': [
                r'hdl\s*(?:cholesterol)?\s*:?\s*(\d+(?:\.\d+)?)',
                r'high\s*density\s*lipoprotein\s*:?\s*(\d+(?:\.\d+)?)',
                r'hdl-c\s*:?\s*(\d+(?:\.\d+)?)',
                r'cholesterol,?\s*hdl\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Triglycerides': [
                r'triglycerides?\s*:?\s*(\d+(?:\.\d+)?)',
                r'trig\s*:?\s*(\d+(?:\.\d+)?)',
                r'tg\s*:?\s*(\d+(?:\.\d+)?)',
                r'trigs?\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Glucose': [
                r'glucose\s*:?\s*(\d+(?:\.\d+)?)',
                r'blood\s*glucose\s*:?\s*(\d+(?:\.\d+)?)',
                r'fasting\s*glucose\s*:?\s*(\d+(?:\.\d+)?)',
                r'gluc\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'HbA1c': [
                r'hba1c\s*:?\s*(\d+(?:\.\d+)?)',
                r'hemoglobin\s*a1c\s*:?\s*(\d+(?:\.\d+)?)',
                r'glycated\s*hemoglobin\s*:?\s*(\d+(?:\.\d+)?)',
                r'a1c\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Creatinine': [
                r'creatinine\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*creatinine\s*:?\s*(\d+(?:\.\d+)?)',
                r'creat\s*:?\s*(\d+(?:\.\d+)?)',
                r'cr\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'BUN': [
                r'bun\s*:?\s*(\d+(?:\.\d+)?)',
                r'blood\s*urea\s*nitrogen\s*:?\s*(\d+(?:\.\d+)?)',
                r'urea\s*nitrogen\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'eGFR': [
                r'egfr\s*:?\s*(\d+(?:\.\d+)?)',
                r'estimated\s*gfr\s*:?\s*(\d+(?:\.\d+)?)',
                r'gfr\s*(?:estimated)?\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Vitamin D': [
                r'vitamin\s*d\s*(?:25\s*oh)?\s*:?\s*(\d+(?:\.\d+)?)',
                r'25\s*(?:oh)?\s*vitamin\s*d\s*:?\s*(\d+(?:\.\d+)?)',
                r'calcidiol\s*:?\s*(\d+(?:\.\d+)?)',
                r'vit\s*d\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Vitamin B12': [
                r'(?:vitamin\s*)?b\s*12\s*:?\s*(\d+(?:\.\d+)?)',
                r'cobalamin\s*:?\s*(\d+(?:\.\d+)?)',
                r'cyanocobalamin\s*:?\s*(\d+(?:\.\d+)?)',
                r'vit\s*b12\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Folate': [
                r'folate\s*:?\s*(\d+(?:\.\d+)?)',
                r'folic\s*acid\s*:?\s*(\d+(?:\.\d+)?)',
                r'vitamin\s*b9\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Iron': [
                r'iron\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*iron\s*:?\s*(\d+(?:\.\d+)?)',
                r'fe\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Ferritin': [
                r'ferritin\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*ferritin\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'TSH': [
                r'tsh\s*:?\s*(\d+(?:\.\d+)?)',
                r'thyroid\s*stimulating\s*hormone\s*:?\s*(\d+(?:\.\d+)?)',
                r'thyrotropin\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'T3': [
                r'(?:free\s*)?t3\s*:?\s*(\d+(?:\.\d+)?)',
                r'triiodothyronine\s*:?\s*(\d+(?:\.\d+)?)',
                r'ft3\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'T4': [
                r'(?:free\s*)?t4\s*:?\s*(\d+(?:\.\d+)?)',
                r'thyroxine\s*:?\s*(\d+(?:\.\d+)?)',
                r'ft4\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Calcium': [
                r'calcium\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*calcium\s*:?\s*(\d+(?:\.\d+)?)',
                r'ca\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Magnesium': [
                r'magnesium\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*magnesium\s*:?\s*(\d+(?:\.\d+)?)',
                r'mg\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Potassium': [
                r'potassium\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*potassium\s*:?\s*(\d+(?:\.\d+)?)',
                r'k\s*:?\s*(\d+(?:\.\d+)?)'
            ],
            'Sodium': [
                r'sodium\s*:?\s*(\d+(?:\.\d+)?)',
                r'serum\s*sodium\s*:?\s*(\d+(?:\.\d+)?)',
                r'na\s*:?\s*(\d+(?:\.\d+)?)'
            ]
        }
    
    def _load_date_patterns(self) -> List[str]:
        """Load date extraction patterns"""
        return [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',
            r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{2,4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4})'
        ]
    
    def _load_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Load unit conversion factors"""
        return {
            'Cholesterol': {
                'mmol/L': 38.67,  # multiply by this to get mg/dL
                'mg/dL': 1.0
            },
            'Glucose': {
                'mmol/L': 18.0,
                'mg/dL': 1.0
            },
            'Creatinine': {
                'μmol/L': 0.0113,
                'mg/dL': 1.0
            }
        }
    
    def _load_clinical_ranges(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Load clinical reference ranges"""
        return {
            'Total Cholesterol': {'normal': (0, 200), 'borderline': (200, 240), 'high': (240, 999)},
            'LDL': {'normal': (0, 100), 'borderline': (100, 160), 'high': (160, 999)},
            'HDL': {'low': (0, 40), 'normal': (40, 999)},
            'Triglycerides': {'normal': (0, 150), 'borderline': (150, 200), 'high': (200, 999)},
            'Glucose': {'normal': (70, 100), 'prediabetic': (100, 126), 'diabetic': (126, 999)},
            'HbA1c': {'normal': (0, 5.7), 'prediabetic': (5.7, 6.5), 'diabetic': (6.5, 999)},
            'Creatinine': {'normal': (0.6, 1.3), 'high': (1.3, 999)},
            'Vitamin D': {'deficient': (0, 20), 'insufficient': (20, 30), 'sufficient': (30, 999)},
            'Vitamin B12': {'deficient': (0, 300), 'low': (300, 400), 'normal': (400, 999)}
        }
    
    def parse_pdf(self, pdf_path: str, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Parse PDF using multiple methods
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs
            
        Returns:
            Dictionary containing extracted biomarker data
        """
        logger.info(f"Parsing PDF: {pdf_path}")
        
        # Try different extraction methods
        extracted_data = {}
        
        # Method 1: pdfplumber (best for text-based PDFs)
        try:
            pdfplumber_data = self._extract_with_pdfplumber(pdf_path)
            if pdfplumber_data:
                extracted_data.update(pdfplumber_data)
                logger.info("Successfully extracted data using pdfplumber")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Method 2: PyPDF2 (fallback for text extraction)
        if not extracted_data:
            try:
                pypdf2_data = self._extract_with_pypdf2(pdf_path)
                if pypdf2_data:
                    extracted_data.update(pypdf2_data)
                    logger.info("Successfully extracted data using PyPDF2")
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        # Method 3: OCR (for scanned PDFs)
        if (not extracted_data or use_ocr):
            try:
                ocr_data = self._extract_with_ocr(pdf_path)
                if ocr_data:
                    extracted_data.update(ocr_data)
                    logger.info("Successfully extracted data using OCR")
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")
        
        # Post-process extracted data
        if extracted_data:
            extracted_data = self._post_process_data(extracted_data)
            logger.info(f"Extracted {len(extracted_data.get('biomarkers', {}))} biomarkers")
        
        return extracted_data
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract data using pdfplumber"""
        extracted_data = {'biomarkers': {}, 'metadata': {}}
        
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            tables = []
            
            for page in pdf.pages:
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            
            # Parse text for biomarkers
            if all_text:
                text_data = self._parse_text_for_biomarkers(all_text)
                extracted_data['biomarkers'].update(text_data.get('biomarkers', {}))
                extracted_data['metadata'].update(text_data.get('metadata', {}))
            
            # Parse tables for biomarkers
            if tables:
                table_data = self._parse_tables_for_biomarkers(tables)
                extracted_data['biomarkers'].update(table_data.get('biomarkers', {}))
        
        return extracted_data
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Extract data using PyPDF2"""
        extracted_data = {'biomarkers': {}, 'metadata': {}}
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            all_text = ""
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
            
            if all_text:
                text_data = self._parse_text_for_biomarkers(all_text)
                extracted_data.update(text_data)
        
        return extracted_data
    
    def _extract_with_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """Extract data using OCR"""
        extracted_data = {'biomarkers': {}, 'metadata': {}}
        
        # Convert PDF to images
        try:
            images = convert_from_path(pdf_path, dpi=300)
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            return extracted_data
        
        all_text = ""
        for i, image in enumerate(images):
            try:
                # Preprocess image for better OCR
                processed_image = self._preprocess_image_for_ocr(image)
                
                # Extract text using OCR
                text = pytesseract.image_to_string(processed_image, config=self.ocr_config)
                all_text += text + "\n"
                
                logger.info(f"OCR processed page {i+1}/{len(images)}")
            except Exception as e:
                logger.warning(f"OCR failed for page {i+1}: {e}")
        
        if all_text:
            text_data = self._parse_text_for_biomarkers(all_text)
            extracted_data.update(text_data)
        
        return extracted_data
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize if too small
        width, height = image.size
        if width < 1000:
            scale_factor = 1000 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _parse_text_for_biomarkers(self, text: str) -> Dict[str, Any]:
        """Parse text and extract biomarker values"""
        text_lower = text.lower()
        extracted_data = {'biomarkers': {}, 'metadata': {}}
        
        # Extract date
        report_date = self._extract_date(text)
        extracted_data['metadata']['report_date'] = report_date
        
        # Extract patient info
        patient_info = self._extract_patient_info(text)
        extracted_data['metadata'].update(patient_info)
        
        # Extract biomarker values
        for biomarker, patterns in self.biomarker_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
                if matches:
                    try:
                        value = float(matches[0])
                        if self._validate_biomarker_value(biomarker, value):
                            extracted_data['biomarkers'][biomarker] = [{
                                'date': report_date,
                                'value': value,
                                'unit': self._extract_unit(text, biomarker),
                                'status': self._get_clinical_status(biomarker, value)
                            }]
                            break  # Use first valid match
                    except (ValueError, IndexError):
                        continue
        
        return extracted_data
    
    def _parse_tables_for_biomarkers(self, tables: List[List[List[str]]]) -> Dict[str, Any]:
        """Parse tables for biomarker data"""
        extracted_data = {'biomarkers': {}}
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Convert table to DataFrame for easier processing
            df = pd.DataFrame(table[1:], columns=table[0])
            
            # Look for biomarker columns
            for col in df.columns:
                if not col:
                    continue
                
                col_lower = col.lower().strip()
                
                # Check if column matches any biomarker
                for biomarker, patterns in self.biomarker_patterns.items():
                    for pattern in patterns:
                        # Create a simpler pattern for column matching
                        simple_pattern = pattern.replace(r'\s*:?\s*(\d+(?:\.\d+)?)', '').replace(r'(?:', '').replace(r')?', '')
                        if re.search(simple_pattern, col_lower, re.IGNORECASE):
                            # Extract values from this column
                            for _, row in df.iterrows():
                                try:
                                    value_str = str(row[col]).strip()
                                    # Extract numeric value
                                    value_match = re.search(r'(\d+(?:\.\d+)?)', value_str)
                                    if value_match:
                                        value = float(value_match.group(1))
                                        if self._validate_biomarker_value(biomarker, value):
                                            if biomarker not in extracted_data['biomarkers']:
                                                extracted_data['biomarkers'][biomarker] = []
                                            
                                            # Try to find date in the same row
                                            date = self._extract_date_from_row(row)
                                            
                                            extracted_data['biomarkers'][biomarker].append({
                                                'date': date,
                                                'value': value,
                                                'unit': self._extract_unit_from_cell(value_str),
                                                'status': self._get_clinical_status(biomarker, value)
                                            })
                                except (ValueError, AttributeError):
                                    continue
                            break
        
        return extracted_data
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0]
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d', 
                               '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%y', '%m-%d-%y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                    
                    # Try parsing month names
                    if any(month in date_str.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                                                                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                        try:
                            parsed_date = datetime.strptime(date_str, '%b %d, %Y')
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            try:
                                parsed_date = datetime.strptime(date_str, '%d %b %Y')
                                return parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                pass
                except Exception:
                    pass
        
        # Default to current date if no date found
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_date_from_row(self, row: pd.Series) -> str:
        """Extract date from table row"""
        for value in row.values:
            if value and isinstance(value, str):
                date = self._extract_date(value)
                if date != datetime.now().strftime('%Y-%m-%d'):  # Not default date
                    return date
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_patient_info(self, text: str) -> Dict[str, str]:
        """Extract patient information from text"""
        info = {}
        
        # Extract name
        name_patterns = [
            r'patient\s*(?:name)?:?\s*([a-zA-Z\s]+)',
            r'name:?\s*([a-zA-Z\s]+)',
            r'patient:?\s*([a-zA-Z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not any(char.isdigit() for char in name):
                    info['patient_name'] = name
                    break
        
        # Extract age
        age_patterns = [
            r'age:?\s*(\d+)',
            r'(\d+)\s*years?\s*old',
            r'(\d+)\s*yo'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 0 < age < 150:  # Reasonable age range
                    info['patient_age'] = str(age)
                    break
        
        # Extract gender
        gender_patterns = [
            r'gender:?\s*(male|female|m|f)',
            r'sex:?\s*(male|female|m|f)',
            r'\b(male|female)\b'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender = match.group(1).upper()
                if gender in ['MALE', 'M']:
                    info['patient_gender'] = 'M'
                elif gender in ['FEMALE', 'F']:
                    info['patient_gender'] = 'F'
                break
        
        return info
    
    def _extract_unit(self, text: str, biomarker: str) -> str:
        """Extract unit for biomarker from text"""
        # Common units for different biomarkers
        unit_patterns = {
            'cholesterol': r'(mg/dl|mmol/l)',
            'glucose': r'(mg/dl|mmol/l)',
            'creatinine': r'(mg/dl|μmol/l|umol/l)',
            'vitamin d': r'(ng/ml|nmol/l)',
            'vitamin b12': r'(pg/ml|pmol/l)',
            'hba1c': r'(%|mmol/mol)'
        }
        
        biomarker_lower = biomarker.lower()
        for key, pattern in unit_patterns.items():
            if key in biomarker_lower:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return ''
    
    def _extract_unit_from_cell(self, cell_value: str) -> str:
        """Extract unit from table cell"""
        unit_match = re.search(r'(\w+/\w+|%)', cell_value)
        return unit_match.group(1) if unit_match else ''
    
    def _validate_biomarker_value(self, biomarker: str, value: float) -> bool:
        """Validate if biomarker value is reasonable"""
        # Define reasonable ranges for validation
        validation_ranges = {
            'Total Cholesterol': (50, 1000),
            'LDL': (20, 800),
            'HDL': (10, 200),
            'Triglycerides': (20, 2000),
            'Glucose': (30, 800),
            'HbA1c': (3.0, 20.0),
            'Creatinine': (0.1, 20.0),
            'Vitamin D': (1, 200),
            'Vitamin B12': (50, 5000),
            'TSH': (0.01, 100.0),
            'Iron': (10, 500),
            'Ferritin': (1, 5000)
        }
        
        if biomarker in validation_ranges:
            min_val, max_val = validation_ranges[biomarker]
            return min_val <= value <= max_val
        
        return True  # Allow unknown biomarkers
    
    def _get_clinical_status(self, biomarker: str, value: float) -> str:
        """Get clinical status for biomarker value"""
        if biomarker not in self.clinical_ranges:
            return 'Unknown'
        
        ranges = self.clinical_ranges[biomarker]
        
        for status, (min_val, max_val) in ranges.items():
            if min_val <= value <= max_val:
                return status.title()
        
        return 'Out of range'
    
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extracted data"""
        if 'biomarkers' not in data:
            return data
        
        # Remove duplicates and sort by date
        for biomarker in data['biomarkers']:
            values = data['biomarkers'][biomarker]
            if isinstance(values, list) and len(values) > 1:
                # Remove duplicates based on date and value
                unique_values = []
                seen = set()
                for item in values:
                    key = (item['date'], item['value'])
                    if key not in seen:
                        unique_values.append(item)
                        seen.add(key)
                
                # Sort by date
                unique_values.sort(key=lambda x: x['date'])
                data['biomarkers'][biomarker] = unique_values
        
        return data
    
    def save_to_json(self, data: Dict[str, Any], output_path: str) -> None:
        """Save extracted data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Data saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")
            raise
    
    def save_to_csv(self, data: Dict[str, Any], output_path: str) -> None:
        """Save biomarker data to CSV file"""
        try:
            records = []
            metadata = data.get('metadata', {})
            
            for biomarker, values in data.get('biomarkers', {}).items():
                if isinstance(values, list):
                    for item in values:
                        record = {
                            'biomarker': biomarker,
                            'date': item.get('date', ''),
                            'value': item.get('value', ''),
                            'unit': item.get('unit', ''),
                            'status': item.get('status', ''),
                            'patient_name': metadata.get('patient_name', ''),
                            'patient_age': metadata.get('patient_age', ''),
                            'patient_gender': metadata.get('patient_gender', ''),
                            'report_date': metadata.get('report_date', '')
                        }
                        records.append(record)
            
            if records:
                df = pd.DataFrame(records)
                df.to_csv(output_path, index=False)
                logger.info(f"Data saved to CSV: {output_path}")
            else:
                logger.warning("No data to save to CSV")
                
        except Exception as e:
            logger.error(f"Failed to save data to CSV: {e}")
            raise
    
    def generate_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend analysis for biomarkers with multiple values"""
        trends = {}
        
        for biomarker, values in data.get('biomarkers', {}).items():
            if isinstance(values, list) and len(values) > 1:
                # Sort by date
                sorted_values = sorted(values, key=lambda x: x['date'])
                
                # Calculate trend
                dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in sorted_values]
                numeric_values = [item['value'] for item in sorted_values]
                
                if len(numeric_values) >= 2:
                    # Simple linear trend
                    x = np.arange(len(numeric_values))
                    coefficients = np.polyfit(x, numeric_values, 1)
                    slope = coefficients[0]
                    
                    # Calculate percentage change
                    first_value = numeric_values[0]
                    last_value = numeric_values[-1]
                    percent_change = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
                    
                    # Determine trend direction
                    if abs(slope) < 0.1:  # Minimal change threshold
                        trend_direction = 'stable'
                    elif slope > 0:
                        trend_direction = 'increasing'
                    else:
                        trend_direction = 'decreasing'
                    
                    trends[biomarker] = {
                        'trend_direction': trend_direction,
                        'slope': round(slope, 4),
                        'percent_change': round(percent_change, 2),
                        'data_points': len(numeric_values),
                        'date_range': f"{sorted_values[0]['date']} to {sorted_values[-1]['date']}",
                        'latest_value': last_value,
                        'latest_status': sorted_values[-1].get('status', 'Unknown')
                    }
        
        return trends
    
    def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable summary report"""
        report_lines = []
        report_lines.append("=== HEALTH BIOMARKER ANALYSIS REPORT ===\n")
        
        # Metadata section
        metadata = data.get('metadata', {})
        if metadata:
            report_lines.append("PATIENT INFORMATION:")
            if 'patient_name' in metadata:
                report_lines.append(f"  Name: {metadata['patient_name']}")
            if 'patient_age' in metadata:
                report_lines.append(f"  Age: {metadata['patient_age']}")
            if 'patient_gender' in metadata:
                report_lines.append(f"  Gender: {metadata['patient_gender']}")
            if 'report_date' in metadata:
                report_lines.append(f"  Report Date: {metadata['report_date']}")
            report_lines.append("")
        
        # Biomarkers section
        biomarkers = data.get('biomarkers', {})
        if biomarkers:
            report_lines.append("BIOMARKER RESULTS:")
            
            # Group by category
            categories = {
                'Lipid Profile': ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides'],
                'Diabetes Markers': ['Glucose', 'HbA1c'],
                'Kidney Function': ['Creatinine', 'BUN', 'eGFR'],
                'Vitamins': ['Vitamin D', 'Vitamin B12', 'Folate'],
                'Thyroid Function': ['TSH', 'T3', 'T4'],
                'Minerals': ['Calcium', 'Magnesium', 'Potassium', 'Sodium', 'Iron', 'Ferritin']
            }
            
            for category, markers in categories.items():
                category_markers = [m for m in markers if m in biomarkers]
                if category_markers:
                    report_lines.append(f"\n{category}:")
                    for marker in category_markers:
                        values = biomarkers[marker]
                        if isinstance(values, list):
                            latest = values[-1]  # Most recent value
                            value_str = f"{latest['value']}"
                            if latest.get('unit'):
                                value_str += f" {latest['unit']}"
                            
                            status_indicator = ""
                            status = latest.get('status', '').lower()
                            if status in ['high', 'diabetic', 'deficient']:
                                status_indicator = " ⚠️"
                            elif status in ['normal', 'sufficient']:
                                status_indicator = " ✓"
                            
                            report_lines.append(f"  {marker}: {value_str} ({latest.get('status', 'Unknown')}){status_indicator}")
            
            # Add uncategorized biomarkers
            uncategorized = []
            all_categorized = []
            for markers in categories.values():
                all_categorized.extend(markers)
            
            for marker in biomarkers:
                if marker not in all_categorized:
                    uncategorized.append(marker)
            
            if uncategorized:
                report_lines.append(f"\nOther Markers:")
                for marker in uncategorized:
                    values = biomarkers[marker]
                    if isinstance(values, list):
                        latest = values[-1]
                        value_str = f"{latest['value']}"
                        if latest.get('unit'):
                            value_str += f" {latest['unit']}"
                        report_lines.append(f"  {marker}: {value_str} ({latest.get('status', 'Unknown')})")
        
        # Trend analysis
        trends = self.generate_trend_analysis(data)
        if trends:
            report_lines.append(f"\nTREND ANALYSIS:")
            for biomarker, trend_data in trends.items():
                direction_emoji = {
                    'increasing': '📈',
                    'decreasing': '📉',
                    'stable': '➡️'
                }.get(trend_data['trend_direction'], '❓')
                
                report_lines.append(f"  {biomarker}: {trend_data['trend_direction'].title()} {direction_emoji}")
                report_lines.append(f"    Change: {trend_data['percent_change']:+.1f}% over {trend_data['data_points']} readings")
        
        # Recommendations section
        report_lines.append(f"\nRECOMMENDations:")
        recommendations = self._generate_recommendations(data)
        for rec in recommendations:
            report_lines.append(f"  • {rec}")
        
        if not recommendations:
            report_lines.append("  • Consult with your healthcare provider for personalized recommendations")
        
        report_lines.append(f"\n{'='*50}")
        report_lines.append("Note: This analysis is for informational purposes only.")
        report_lines.append("Always consult with qualified healthcare professionals for medical advice.")
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate basic health recommendations based on biomarker values"""
        recommendations = []
        biomarkers = data.get('biomarkers', {})
        
        # Check for common issues and generate recommendations
        for biomarker, values in biomarkers.items():
            if not isinstance(values, list) or not values:
                continue
                
            latest = values[-1]
            status = latest.get('status', '').lower()
            value = latest.get('value', 0)
            
            if biomarker == 'Total Cholesterol' and status == 'high':
                recommendations.append("Consider dietary changes to reduce cholesterol intake")
            elif biomarker == 'LDL' and status == 'high':
                recommendations.append("Focus on reducing saturated fats and increasing fiber intake")
            elif biomarker == 'HDL' and status == 'low':
                recommendations.append("Increase physical activity to boost HDL cholesterol")
            elif biomarker == 'Triglycerides' and status == 'high':
                recommendations.append("Limit refined carbohydrates and added sugars")
            elif biomarker in ['Glucose', 'HbA1c'] and status in ['prediabetic', 'diabetic']:
                recommendations.append("Monitor blood sugar levels and consider diabetes management strategies")
            elif biomarker == 'Vitamin D' and status in ['deficient', 'insufficient']:
                recommendations.append("Consider vitamin D supplementation and increased sun exposure")
            elif biomarker == 'Vitamin B12' and status == 'deficient':
                recommendations.append("Consider vitamin B12 supplementation or B12-rich foods")
            elif biomarker == 'Creatinine' and status == 'high':
                recommendations.append("Stay well-hydrated and monitor kidney function")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations[:5]  # Limit to 5 recommendations
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update patterns if provided
            if 'biomarker_patterns' in config:
                self.biomarker_patterns.update(config['biomarker_patterns'])
            
            # Update clinical ranges if provided
            if 'clinical_ranges' in config:
                self.clinical_ranges.update(config['clinical_ranges'])
            
            # Update OCR config if provided
            if 'ocr_config' in config:
                self.ocr_config = config['ocr_config']
            
            logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Advanced PDF Parser for Health Reports')
    parser.add_argument('pdf_file', help='Path to PDF file to parse')
    parser.add_argument('-o', '--output', help='Output file path (JSON format)', default='output.json')
    parser.add_argument('--csv', help='Also save as CSV file', action='store_true')
    parser.add_argument('--ocr', help='Force OCR processing', action='store_true')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--report', help='Generate summary report', action='store_true')
    parser.add_argument('--verbose', '-v', help='Verbose logging', action='store_true')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_file):
        print(f"Error: PDF file '{args.pdf_file}' not found")
        sys.exit(1)
    
    try:
        # Initialize parser
        parser_instance = AdvancedPDFParser(config_file=args.config)
        
        # Parse PDF
        print(f"Parsing PDF: {args.pdf_file}")
        extracted_data = parser_instance.parse_pdf(args.pdf_file, use_ocr=args.ocr)
        
        if not extracted_data or not extracted_data.get('biomarkers'):
            print("Warning: No biomarker data extracted from PDF")
        else:
            print(f"Successfully extracted {len(extracted_data['biomarkers'])} biomarkers")
        
        # Save to JSON
        parser_instance.save_to_json(extracted_data, args.output)
        
        # Save to CSV if requested
        if args.csv:
            csv_path = args.output.replace('.json', '.csv')
            parser_instance.save_to_csv(extracted_data, csv_path)
        
        # Generate report if requested
        if args.report:
            report = parser_instance.generate_summary_report(extracted_data)
            report_path = args.output.replace('.json', '_report.txt')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Summary report saved to: {report_path}")
            
            # Also print to console
            print("\n" + "="*50)
            print(report)
        
        print(f"\nExtraction completed successfully!")
        print(f"Output saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Error during PDF parsing: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
        