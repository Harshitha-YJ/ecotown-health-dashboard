// Global variables
let currentChart = null;
let healthData = {};
let currentBiomarker = 'lipid';
let showNormalRanges = true;


const clinicalRanges = {
    'Total Cholesterol': { normal: [0, 200], borderline: [200, 240], high: [240, 999], unit: 'mg/dL' },
    'LDL': { normal: [0, 100], borderline: [100, 160], high: [160, 999], unit: 'mg/dL' },
    'HDL': { normal: [40, 999], low: [0, 40], unit: 'mg/dL' },
    'Triglycerides': { normal: [0, 150], borderline: [150, 200], high: [200, 999], unit: 'mg/dL' },
    'Creatinine': { normal: [0.6, 1.3], high: [1.3, 999], unit: 'mg/dL' },
    'Vitamin D': { deficient: [0, 20], insufficient: [20, 30], sufficient: [30, 999], unit: 'ng/mL' },
    'Vitamin B12': { deficient: [0, 300], low: [300, 400], normal: [400, 999], unit: 'pg/mL' },
    'HbA1c': { normal: [0, 5.7], prediabetic: [5.7, 6.5], diabetic: [6.5, 999], unit: '%' }
};


// Load sample data from JSON file
async function loadSampleData() {
    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('assets/data/sample-data.json');
        const data = await response.json();
        healthData = data.biomarkers;
        updateDashboard();
        Utils.showNotification('Sample data loaded successfully!', 'success');
    } catch (err) {
        console.error("Error loading sample data:", err);
        Utils.showNotification('Failed to load sample data.', 'error');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Update the full dashboard
function updateDashboard() {
    updateChart(currentBiomarker);
    renderCards(currentBiomarker);
    renderInsights(currentBiomarker);
}

// Update the main chart
function updateChart(profileType) {
    const canvas = document.getElementById('mainChart');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if exists
    if (currentChart) {
        currentChart.destroy();
    }

    // (Continue your chart setup logic here...)

    const biomarkerGroups = {
        lipid: ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides'],
        kidney: ['Creatinine'],
        vitamins: ['Vitamin D', 'Vitamin B12'],
        diabetes: ['HbA1c'],
        all: Object.keys(healthData)
    };

    const biomarkers = biomarkerGroups[profileType] || [];

    const datasets = biomarkers.map((biomarker, index) => {
        const data = healthData[biomarker] || [];
        return {
            label: biomarker,
            data: data.map(point => ({
                x: point.date,
                y: point.value
            })),
            borderColor: Utils.getColorPalette(biomarkers.length)[index],
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.3,
            pointRadius: 4
        };
    });

    const config = new ChartConfig().getMultiLineChartConfig(biomarkers);
    config.data = { datasets };

    currentChart = new Chart(ctx, {
        type: 'line',
        data: config.data,
        options: config
    });
}

// Render biomarker cards
function renderCards(profileType) {
    const container = document.getElementById('biomarkerCards');
    container.innerHTML = '';

    const biomarkerGroups = {
        lipid: ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides'],
        kidney: ['Creatinine'],
        vitamins: ['Vitamin D', 'Vitamin B12'],
        diabetes: ['HbA1c'],
        all: Object.keys(healthData)
    };

    const biomarkers = biomarkerGroups[profileType] || [];

    biomarkers.forEach(biomarker => {
        const data = healthData[biomarker];
        if (!data || data.length === 0) return;

        const latest = data[data.length - 1];
        const trend = Utils.calculateTrend(data);
        const range = clinicalRanges[biomarker] || {};
        let rangeClass = 'range-normal';

        if (range.high && latest.value >= range.high[0]) {
            rangeClass = 'range-danger';
        } else if (range.borderline && latest.value >= range.borderline[0]) {
            rangeClass = 'range-warning';
        }

        const trendIcon = trend?.direction === 'up' ? '↑' : trend?.direction === 'down' ? '↓' : '→';
        const trendClass = trend?.direction === 'up' ? 'trend-up' :
                           trend?.direction === 'down' ? 'trend-down' :
                           'trend-stable';

        container.innerHTML += `
            <div class="biomarker-card">
                <div class="card-header">
                    <div class="card-title">${biomarker}</div>
                </div>
                <div class="card-value">${Utils.formatNumber(latest.value)} ${range.unit || ''}</div>
                <div class="card-trend ${trendClass}">
                    ${trendIcon} ${Utils.formatNumber(trend?.percentChange || 0)}%
                </div>
                <div class="range-indicator">
                    <div class="range-fill ${rangeClass}" style="width: 100%;"></div>
                </div>
            </div>
        `;
    });
}

// Render insights
function renderInsights(profileType) {
    const container = document.getElementById('insights');
    container.innerHTML = '';

    const biomarkerGroups = {
        lipid: ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides'],
        kidney: ['Creatinine'],
        vitamins: ['Vitamin D', 'Vitamin B12'],
        diabetes: ['HbA1c'],
        all: Object.keys(healthData)
    };

    const biomarkers = biomarkerGroups[profileType] || [];

    biomarkers.forEach(biomarker => {
        const data = healthData[biomarker];
        if (!data || data.length === 0) return;

        const latest = data[data.length - 1];
        const range = clinicalRanges[biomarker] || {};
        let status = 'Normal';
        let css = 'insight-normal';

        if (range.high && latest.value >= range.high[0]) {
            status = 'High';
            css = 'insight-danger';
        } else if (range.borderline && latest.value >= range.borderline[0]) {
            status = 'Borderline';
            css = 'insight-warning';
        } else if (range.low && latest.value < range.low[1]) {
            status = 'Low';
            css = 'insight-warning';
        } else if (range.deficient && latest.value < range.deficient[1]) {
            status = 'Deficient';
            css = 'insight-danger';
        }

        container.innerHTML += `
            <div class="insight-item">
                <div class="insight-icon ${css}">●</div>
                <div class="insight-text">
                    ${biomarker} is currently <strong>${status}</strong> at ${Utils.formatNumber(latest.value)} ${range.unit || ''}
                </div>
            </div>
        `;
    });
}

// Event handler for switching biomarkers
function switchBiomarker(type) {
    currentBiomarker = type;
    updateDashboard();

    // Clear previous active button
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Set active button based on the type
    const tabMap = {
        lipid: 0,
        kidney: 1,
        vitamins: 2,
        diabetes: 3,
        all: 4
    };

    const index = tabMap[type];
    const buttons = document.querySelectorAll('.tab-button');

    if (buttons[index]) {
        buttons[index].classList.add('active');
    }
}


// Export buttons
function exportChart(format) {
    const link = document.createElement('a');
    if (format === 'png') {
        link.href = document.getElementById('mainChart').toDataURL('image/png');
        link.download = 'biomarker-chart.png';
    } else if (format === 'pdf') {
        const pdf = new window.jspdf.jsPDF();
        pdf.addImage(document.getElementById('mainChart').toDataURL('image/png'), 'PNG', 10, 10, 180, 100);
        pdf.save('biomarker-chart.pdf');
        return;
    }
    link.click();
}

function exportData() {
    Utils.exportToCSV(healthData);
}

// Time range buttons (not implemented fully here)
function setTimeRange(range) {
    Utils.showNotification(`Time range "${range}" selected (not implemented)`, 'info');
}

// Toggle clinical ranges (not implemented fully here)
function toggleNormalRanges() {
    showNormalRanges = !showNormalRanges;
    updateDashboard();
}

function handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const processor = new DataProcessor();
    const file = files[0];

    if (Utils.validateFileType(file, ['pdf', 'csv', 'json'])) {
        document.getElementById('loading').style.display = 'block';

        const processPromise = file.name.endsWith('.csv') ?
            processor.processCSVFile(file) :
            file.name.endsWith('.json') ?
            loadJSONFile(file) :
            processor.processPDFFile(file);

        processPromise.then(data => {
            healthData = data;
            updateDashboard();
            Utils.showNotification("Health report uploaded!", "success");
        }).catch(err => {
            console.error("Upload failed:", err);
            Utils.showNotification("Failed to process uploaded file.", "error");
        }).finally(() => {
            document.getElementById('loading').style.display = 'none';
        });
    } else {
        Utils.showNotification("Unsupported file format.", "warning");
    }
}

function loadJSONFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const json = JSON.parse(e.target.result);
                resolve(json.biomarkers || {});
            } catch (err) {
                reject(err);
            }
        };
        reader.onerror = reject;
        reader.readAsText(file);
    });
}
function switchBiomarker(type) {
    currentBiomarker = type;
    updateDashboard();

    // Remove 'active' class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Add 'active' class to the clicked button
    const clickedButton = Array.from(document.querySelectorAll('.tab-button')).find(btn =>
        btn.textContent.toLowerCase().includes(type)
    );
    if (clickedButton) clickedButton.classList.add('active');
}
