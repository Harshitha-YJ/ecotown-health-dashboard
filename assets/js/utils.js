 // Utility functions for EcoTown Health Dashboard

class Utils {
    // Format numbers with proper precision
    static formatNumber(value, decimals = 1) {
        if (typeof value !== 'number' || isNaN(value)) return 'N/A';
        return value.toFixed(decimals);
    }

    // Format dates consistently
    static formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return dateString;
        }
    }

    // Calculate trend (positive/negative change)
    static calculateTrend(data) {
        if (!data || data.length < 2) return null;
        
        const latest = data[data.length - 1].value;
        const previous = data[data.length - 2].value;
        const change = latest - previous;
        const percentChange = (change / previous) * 100;
        
        return {
            change: change,
            percentChange: percentChange,
            direction: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
        };
    }

    // Generate color palette for charts
    static getColorPalette(count) {
        const colors = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
            '#8B5CF6', '#06B6D4', '#F97316', '#84CC16',
            '#EC4899', '#6366F1', '#14B8A6', '#F472B6'
        ];
        
        return colors.slice(0, count);
    }

    // Debounce function for search/filter inputs
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Validate file types
    static validateFileType(file, allowedTypes = ['pdf', 'csv', 'json']) {
        const extension = file.name.split('.').pop().toLowerCase();
        return allowedTypes.includes(extension);
    }

    // Convert file size to human readable format
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Show notification messages
    static showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close">&times;</button>
            </div>
            `;

        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Add styles if not already present
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 16px;
                    border-radius: 8px;
                    color: white;
                    z-index: 1000;
                    animation: slideIn 0.3s ease-out;
                }
                .notification-info { background-color: #3B82F6; }
                .notification-success { background-color: #10B981; }
                .notification-warning { background-color: #F59E0B; }
                .notification-error { background-color: #EF4444; }
                .notification-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px;
                }
                .notification-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    margin: 0;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Auto remove
        setTimeout(() => {
            notification.remove();
        }, duration);
        
        // Manual close
        notification.querySelector('.notification-close').onclick = () => {
            notification.remove();
        };
    }

    // Export data to CSV
    static exportToCSV(data, filename = 'biomarker-data.csv') {
        let csvContent = 'Date';
        const biomarkers = Object.keys(data);
        biomarkers.forEach(biomarker => {
            csvContent += ',' + biomarker;
        });
        csvContent += '\n';
        
        // Get all unique dates
        const allDates = new Set();
        biomarkers.forEach(biomarker => {
            data[biomarker].forEach(point => {
                allDates.add(point.date);
            });
        });
        
        // Sort dates
        const sortedDates = Array.from(allDates).sort();
        
        // Create CSV rows
        sortedDates.forEach(date => {
            let row = date;
            biomarkers.forEach(biomarker => {
                const point = data[biomarker].find(p => p.date === date);
                row += ',' + (point ? point.value : '');
            });
            csvContent += row + '\n';
        });
        
        // Download file
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // Generate PDF report (basic implementation)
    static generatePDFReport(data, patientInfo) {
        // This would require a PDF library like jsPDF
        // For now, create a printable HTML version
        const reportWindow = window.open('', '_blank');
        const reportHTML = `
            
            
            
                Biomarker Report - ${patientInfo.name}
                
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .patient-info { background: #f5f5f5; padding: 20px; margin-bottom: 30px; }
                    .biomarker-section { margin-bottom: 20px; }
                    .biomarker-title { font-weight: bold; color: #2563eb; }
                    .values { margin-left: 20px; }
                    @media print { body { margin: 20px; } }
                
            
            
                
                    Biomarker Analysis Report
                    Generated on ${new Date().toLocaleDateString()}
                
                
                
                    Patient Information
                    Name: ${patientInfo.name}
                    Age: ${patientInfo.age}
                    Gender: ${patientInfo.gender}
                    Last Updated: ${patientInfo.last_updated}
                
                
                
                    Biomarker Values
                    ${Object.keys(data).map(biomarker => `
                        
                            ${biomarker}
                            
                                Latest Value: ${data[biomarker][data[biomarker].length - 1].value}
                                (${data[biomarker][data[biomarker].length - 1].date})
                            
                        
                    `).join('')}
                
                
                window.print();
            
            
        `;
        
        reportWindow.document.write(reportHTML);
        reportWindow.document.close();
    }
}

// Export for global use
window.Utils = Utils;
