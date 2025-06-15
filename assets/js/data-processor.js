class DataProcessor {
    constructor() {
        this.clinicalRanges = {
            'Total Cholesterol': { normal: [0, 200], borderline: [200, 240], high: [240, 999], unit: 'mg/dL' },
            'LDL': { normal: [0, 100], borderline: [100, 160], high: [160, 999], unit: 'mg/dL' },
            'HDL': { normal: [40, 999], low: [0, 40], unit: 'mg/dL' },
            'Triglycerides': { normal: [0, 150], borderline: [150, 200], high: [200, 999], unit: 'mg/dL' },
            'Creatinine': { normal: [0.6, 1.3], high: [1.3, 999], unit: 'mg/dL' },
            'Vitamin D': { deficient: [0, 20], insufficient: [20, 30], sufficient: [30, 999], unit: 'ng/mL' },
            'Vitamin B12': { deficient: [0, 300], low: [300, 400], normal: [400, 999], unit: 'pg/mL' },
            'HbA1c': { normal: [0, 5.7], prediabetic: [5.7, 6.5], diabetic: [6.5, 999], unit: '%' }
        };
    }

    // Process uploaded PDF files
    async processPDFFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                // Simulate PDF parsing - in real implementation, use PDF.js
                const extractedData = this.simulatePDFExtraction(file.name);
                resolve(extractedData);
            };
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    // Process CSV files
    async processCSVFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const csv = e.target.result;
                const data = this.parseCSV(csv);
                resolve(data);
            };
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    // Parse CSV data
    parseCSV(csv) {
        const lines = csv.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = {};

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            if (values.length === headers.length) {
                const date = values[0];
                for (let j = 1; j < headers.length; j++) {
                    const biomarker = headers[j];
                    const value = parseFloat(values[j]);
                    
                    if (!data[biomarker]) {
                        data[biomarker] = [];
                    }
                    
                    data[biomarker].push({
                        date: date,
                        value: value
                    });
                }
            }
        }

        return data;
    }

    // Simulate PDF data extraction
    simulatePDFExtraction(filename) {
        // This would normally use OCR or PDF parsing
        // For demo, return random data based on filename
        const biomarkers = ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides', 'Creatinine', 'Vitamin D', 'Vitamin B12', 'HbA1c'];
        const data = {};
        
        biomarkers.forEach(biomarker => {
            data[biomarker] = [{
                date: new Date().toISOString().split('T')[0],
                value: this.generateRandomValue(biomarker)
            }];
        });

        return data;
    }

    // Generate random values within normal ranges
    generateRandomValue(biomarker) {
        const ranges = {
            'Total Cholesterol': [150, 220],
            'LDL': [80, 130],
            'HDL': [40, 70],
            'Triglycerides': [100, 180],
            'Creatinine': [0.7, 1.2],
            'Vitamin D': [25, 45],
            'Vitamin B12': [300, 600],
            'HbA1c': [4.5, 6.2]
        };

        const range = ranges[biomarker] || [0, 100];
        return Math.random() * (range[1] - range[0]) + range[0];
    }

    // Validate biomarker data
    validateData(data) {
        const errors = [];
        
        Object.keys(data).forEach(biomarker => {
            if (!this.clinicalRanges[biomarker]) {
                errors.push(`Unknown biomarker: ${biomarker}`);
                return;
            }

            data[biomarker].forEach(point => {
                if (!point.date || !point.value) {
                    errors.push(`Invalid data point for ${biomarker}`);
                }
                
                if (isNaN(point.value) || point.value < 0) {
                    errors.push(`Invalid value for ${biomarker}: ${point.value}`);
                }
            });
        });

        return errors;
    }
}

// Export for use in other modules
window.DataProcessor = DataProcessor;