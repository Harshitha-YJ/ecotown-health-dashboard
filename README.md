# EcoTown Health Dashboard Documentation

The **EcoTown Health Dashboard** is a web-based application that allows users to upload clinical health reports (in PDF format), extract biomarker data, and visualize it through interactive charts. This empowers users to understand and monitor their health metrics effectively.

## 📌 Purpose

To provide a simple and intuitive health report dashboard for users based on their lab report PDFs. It highlights key health indicators, shows how they compare with clinical reference ranges, and helps users track their wellness over time.

## 🧩 Key Features

- Upload PDF health reports directly through the web interface
- Automatically extract biomarker data using `pdfplumber`
- Visualize values using Chart.js with intuitive line and bar graphs
- Compare with standard clinical reference ranges
- Responsive and mobile-friendly frontend design

## ⚙️ Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (Chart.js for visualization)
- **Backend**: Python (Flask framework)
- **PDF Parsing**: pdfplumber
- **Others**: Bootstrap (for styling), GitHub (for version control and hosting)

## 🔧 Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ecotown-health-dashboard.git
   cd ecotown-health-dashboard
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask backend server:
   ```bash
   python app.py
   ```

5. Open `index.html` in your web browser (or serve via Flask if templated).

## 📁 Project Structure

```
ecotown-health-dashboard/
├── index.html                 # Main dashboard file
├── assets/
│   ├── css/
│   │   └── styles.css        # Additional styles
│   ├── js/
│   │   ├── chart-config.js   # Chart configurations
│   │   ├── data-processor.js # Data processing logic
│   │   └── utils.js          # Utility functions
        └──  app.js            
                  
│   └── data/
│       ├── sample-data.json  # Sample biomarker data
│       └── uploads/          # Uploaded files directory
├── docs/
│   ├── README.md             # Project documentation
│   ├── API.md                # API documentation
│   └── clinical-ranges.md    # Clinical reference ranges
├── scripts/
│   ├── data-extractor.py     # Python data extraction script
│   └── pdf-parser.py         # PDF parsing script
├── tests/
│   ├── test-data.json        # Test datasets
│   └── test-cases.md         # Test scenarios
├── package.json              # Dependencies (if using npm)
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
└── deploy/
    ├── vercel.json          # Vercel deployment config
    ├── netlify.toml         # Netlify deployment config

```

## 🙋 Support

For any issues, please open an issue on the GitHub repository.

## Features After Uploading a Report

Once a health report is uploaded and successfully parsed:
- 📊 An interactive chart is displayed in the main panel.
- 📌 A summary box appears in the bottom-left corner showing:
  - The patient's name and report date.
  - Health flags (normal/abnormal indicators) for each biomarker.
- 🔍 Detailed reference ranges are shown beneath the chart for clinical interpretation.
- ✅ You can also test the system using the built-in sample report uploader.

To upload a sample report:
1. Click the **"Upload Sample Report"** button on the top navigation bar.
2. The dashboard will auto-populate with example biomarker data and render all features.

3. To visit website , click on - https://harshitha-yj.github.io/ecotown-health-dashboard/
