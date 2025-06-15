// Chart.js configurations for EcoTown Health Dashboard

class ChartConfig {
    constructor() {
        this.colors = {
            primary: '#3B82F6',
            secondary: '#10B981',
            accent: '#F59E0B',
            danger: '#EF4444',
            warning: '#F97316',
            info: '#06B6D4',
            success: '#22C55E',
            purple: '#8B5CF6'
        };

        this.clinicalRanges = {
            'Total Cholesterol': { 
                normal: [0, 200], 
                borderline: [200, 240], 
                high: [240, 999], 
                unit: 'mg/dL',
                color: this.colors.primary
            },
            'LDL': { 
                normal: [0, 100], 
                borderline: [100, 160], 
                high: [160, 999], 
                unit: 'mg/dL',
                color: this.colors.danger
            },
            'HDL': { 
                normal: [40, 999], 
                low: [0, 40], 
                unit: 'mg/dL',
                color: this.colors.success
            },
            'Triglycerides': { 
                normal: [0, 150], 
                borderline: [150, 200], 
                high: [200, 999], 
                unit: 'mg/dL',
                color: this.colors.warning
            },
            'Creatinine': { 
                normal: [0.6, 1.3], 
                high: [1.3, 999], 
                unit: 'mg/dL',
                color: this.colors.info
            },
            'Vitamin D': { 
                deficient: [0, 20], 
                insufficient: [20, 30], 
                sufficient: [30, 999], 
                unit: 'ng/mL',
                color: this.colors.accent
            },
            'Vitamin B12': { 
                deficient: [0, 300], 
                low: [300, 400], 
                normal: [400, 999], 
                unit: 'pg/mL',
                color: this.colors.purple
            },
            'HbA1c': { 
                normal: [0, 5.7], 
                prediabetic: [5.7, 6.5], 
                diabetic: [6.5, 999], 
                unit: '%',
                color: this.colors.secondary
            }
        };
    }

    // Get base chart configuration
    getBaseConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            family: 'Inter, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#374151',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: (context) => {
                            return Utils.formatDate(context[0].label);
                        },
                        label: (context) => {
                            const biomarker = context.dataset.label;
                            const value = context.parsed.y;
                            const unit = this.clinicalRanges[biomarker]?.unit || '';
                            return `${biomarker}: ${Utils.formatNumber(value)} ${unit}`;
                        },
                        afterLabel: (context) => {
                            const biomarker = context.dataset.label;
                            const value = context.parsed.y;
                            return this.getClinicalStatus(biomarker, value);
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        parser: 'yyyy-MM-dd',
                        tooltipFormat: 'MMM, dd, yyyy',
                        displayFormats: {
                            day: 'MMM dd',
                            week: 'MMM dd',
                            month: 'MMM yyyy'
                        }
                    },
                    grid: {
                        color: 'rgba(156, 163, 175, 0.2)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6B7280',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(156, 163, 175, 0.2)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6B7280',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return Utils.formatNumber(value);
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6,
                    borderWidth: 2,
                    hoverBorderWidth: 3
                },
                line: {
                    borderWidth: 2,
                    tension: 0.2
                }
            }
        };
    }

    // Get configuration for line chart
    getLineChartConfig(data, biomarker) {
        const config = this.getBaseConfig();
        const range = this.clinicalRanges[biomarker];
        
        // Add clinical range annotations
        if (range) {
            config.plugins.annotation = {
                annotations: this.getClinicalRangeAnnotations(biomarker, range)
            };
        }

        // Customize for single biomarker
        config.plugins.title = {
            display: true,
            text: `${biomarker} Trend Analysis`,
            font: {
                size: 16,
                weight: 'bold',
                family: 'Inter, sans-serif'
            },
            color: '#1F2937',
            padding: 20
        };

        // Add unit to y-axis
        if (range && range.unit) {
            config.scales.y.title = {
                display: true,
                text: range.unit,
                color: '#6B7280',
                font: {
                    size: 12,
                    weight: 'bold'
                }
            };
        }

        return config;
    }

    // Get configuration for multi-biomarker comparison
    getMultiLineChartConfig(biomarkers) {
        const config = this.getBaseConfig();
        
        config.plugins.title = {
            display: true,
            text: 'Biomarker Comparison',
            font: {
                size: 16,
                weight: 'bold',
                family: 'Inter, sans-serif'
            },
            color: '#1F2937',
            padding: 20
        };

        // Use normalized scale for comparison
        config.scales.y.title = {
            display: true,
            text: 'Normalized Values',
            color: '#6B7280',
            font: {
                size: 12,
                weight: 'bold'
            }
        };

        return config;
    }

    // Get configuration for scatter plot
    getScatterChartConfig(xBiomarker, yBiomarker) {
        const config = {
            type: 'scatter',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${xBiomarker} vs ${yBiomarker} Correlation`,
                        font: {
                            size: 16,
                            weight: 'bold',
                            family: 'Inter, sans-serif'
                        },
                        color: '#1F2937',
                        padding: 20
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const x = Utils.formatNumber(context.parsed.x);
                                const y = Utils.formatNumber(context.parsed.y);
                                const xUnit = this.clinicalRanges[xBiomarker]?.unit || '';
                                const yUnit = this.clinicalRanges[yBiomarker]?.unit || '';
                                return [`${xBiomarker}: ${x} ${xUnit}`, `${yBiomarker}: ${y} ${yUnit}`];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: `${xBiomarker} (${this.clinicalRanges[xBiomarker]?.unit || ''})`,
                            color: '#6B7280'
                        },
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `${yBiomarker} (${this.clinicalRanges[yBiomarker]?.unit || ''})`,
                            color: '#6B7280'
                        },
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    }
                }
            }
        };

        return config;
    }

    // Get clinical range annotations for charts
    getClinicalRangeAnnotations(biomarker, range) {
        const annotations = {};

        if (range.normal) {
            annotations.normalRange = {
                type: 'box',
                yMin: range.normal[0],
                yMax: range.normal[1],
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderColor: 'rgba(34, 197, 94, 0.3)',
                borderWidth: 1,
                label: {
                    content: 'Normal Range',
                    enabled: true,
                    position: 'start',
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    color: 'white',
                    font: {
                        size: 10
                    }
                }
            };
        }

        if (range.borderline) {
            annotations.borderlineRange = {
                type: 'box',
                yMin: range.borderline[0],
                yMax: range.borderline[1],
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderColor: 'rgba(245, 158, 11, 0.3)',
                borderWidth: 1,
                label: {
                    content: 'Borderline',
                    enabled: true,
                    position: 'center',
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    color: 'white',
                    font: {
                        size: 10
                    }
                }
            };
        }

        if (range.high) {
            annotations.highRange = {
                type: 'box',
                yMin: range.high[0],
                yMax: Math.min(range.high[1], range.high[0] * 2), // Limit visual range
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderColor: 'rgba(239, 68, 68, 0.3)',
                borderWidth: 1,
                label: {
                    content: 'High Risk',
                    enabled: true,
                    position: 'end',
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    color: 'white',
                    font: {
                        size: 10
                    }
                }
            };
        }

        return annotations;
    }

    // Get clinical status for a biomarker value
    getClinicalStatus(biomarker, value) {
        const range = this.clinicalRanges[biomarker];
        if (!range) return '';

        if (range.normal && value >= range.normal[0] && value <= range.normal[1]) {
            return '✓ Normal';
        }
        if (range.borderline && value >= range.borderline[0] && value <= range.borderline[1]) {
            return '⚠ Borderline';
        }
        if (range.high && value >= range.high[0]) {
            return '⚠ High';
        }
        if (range.low && value <= range.low[1]) {
            return '⚠ Low';
        }
        if (range.deficient && value >= range.deficient[0] && value <= range.deficient[1]) {
            return '⚠ Deficient';
        }
        if (range.insufficient && value >= range.insufficient[0] && value <= range.insufficient[1]) {
            return '⚠ Insufficient';
        }
        if (range.sufficient && value >= range.sufficient[0]) {
            return '✓ Sufficient';
        }
        if (range.prediabetic && value >= range.prediabetic[0] && value <= range.prediabetic[1]) {
            return '⚠ Pre-diabetic';
        }
        if (range.diabetic && value >= range.diabetic[0]) {
            return '⚠ Diabetic';
        }

        return '';
    }

    // Create dataset for Chart.js
    createDataset(biomarker, data, options = {}) {
        const range = this.clinicalRanges[biomarker];
        const color = range?.color || this.colors.primary;

        return {
            label: biomarker,
            data: data.map(point => ({
                x: point.date,
                y: point.value
            })),
            borderColor: color,
            backgroundColor: color + '20', // 20% opacity
            pointBackgroundColor: color,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            fill: options.fill || false,
            tension: options.tension || 0.2,
            ...options
        };
    }

    // Create multiple datasets for comparison
    createMultipleDatasets(biomarkersData, options = {}) {
        const datasets = [];
        const colors = Object.values(this.colors);
        let colorIndex = 0;

        Object.keys(biomarkersData).forEach(biomarker => {
            const range = this.clinicalRanges[biomarker];
            const color = range?.color || colors[colorIndex % colors.length];
            
            datasets.push(this.createDataset(biomarker, biomarkersData[biomarker], {
                borderColor: color,
                backgroundColor: color + '20',
                pointBackgroundColor: color,
                ...options
            }));
            
            colorIndex++;
        });

        return datasets;
    }

    // Get chart theme based on user preference
    getTheme(isDark = false) {
        if (isDark) {
            return {
                backgroundColor: '#1F2937',
                color: '#F9FAFB',
                gridColor: 'rgba(156, 163, 175, 0.1)',
                tooltipBackground: 'rgba(0, 0, 0, 0.9)'
            };
        }
        
        return {
            backgroundColor: '#FFFFFF',
            color: '#1F2937',
            gridColor: 'rgba(156, 163, 175, 0.2)',
            tooltipBackground: 'rgba(0, 0, 0, 0.8)'
        };
    }

    // Apply theme to chart configuration
    applyTheme(config, isDark = false) {
        const theme = this.getTheme(isDark);
        
        // Update colors in the configuration
        if (config.plugins) {
            if (config.plugins.title) {
                config.plugins.title.color = theme.color;
            }
            if (config.plugins.legend) {
                config.plugins.legend.labels.color = theme.color;
            }
            if (config.plugins.tooltip) {
                config.plugins.tooltip.backgroundColor = theme.tooltipBackground;
            }
        }

        if (config.scales) {
            ['x', 'y'].forEach(axis => {
                if (config.scales[axis]) {
                    if (config.scales[axis].grid) {
                        config.scales[axis].grid.color = theme.gridColor;
                    }
                    if (config.scales[axis].ticks) {
                        config.scales[axis].ticks.color = theme.color;
                    }
                    if (config.scales[axis].title) {
                        config.scales[axis].title.color = theme.color;
                    }
                }
            });
        }

        return config;
    }
}

// Export for global use
window.ChartConfig = ChartConfig;