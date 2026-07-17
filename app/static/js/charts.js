// Colors matching CSS theme
const CHART_COLORS = {
  purple: '#8b5cf6',
  blue: '#3b82f6',
  cyan: '#06b6d4',
  indigo: '#6366f1',
  green: '#10b981',
  yellow: '#fbbf24',
  red: '#f87171'
};

const GRID_COLOR = 'rgba(255, 255, 255, 0.05)';
const TEXT_COLOR = '#94a3b8';

function getStatusColor(status) {
  const s = status.toLowerCase();
  if (s.includes('approve') || s.includes('deliver') || s.includes('mail')) return CHART_COLORS.green;
  if (s.includes('fingerprint') || s.includes('receive')) return CHART_COLORS.blue;
  if (s.includes('evidence') || s.includes('interview') || s.includes('ready')) return CHART_COLORS.yellow;
  if (s.includes('reopen') || s.includes('deny') || s.includes('action')) return CHART_COLORS.red;
  return CHART_COLORS.purple;
}

function createStatusDoughnutChart(ctx, data) {
  const labels = Object.keys(data);
  const values = Object.values(data);
  const backgroundColors = labels.map(label => getStatusColor(label));

  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: backgroundColors,
        borderWidth: 1,
        borderColor: 'rgba(8, 11, 17, 0.8)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: TEXT_COLOR,
            font: { family: 'Plus Jakarta Sans', size: 11 }
          }
        }
      }
    }
  });
}

function createFormTypeBarChart(ctx, data) {
  const labels = Object.keys(data);
  const values = Object.values(data);

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cases',
        data: values,
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
        borderColor: CHART_COLORS.purple,
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: GRID_COLOR },
          ticks: { color: TEXT_COLOR, font: { family: 'Plus Jakarta Sans' } }
        },
        y: {
          grid: { color: GRID_COLOR },
          ticks: { 
            color: TEXT_COLOR, 
            font: { family: 'Plus Jakarta Sans' },
            stepSize: 1,
            precision: 0
          }
        }
      }
    }
  });
}

function createTimelineLineChart(ctx, data) {
  const labels = data.labels || [];
  const values = data.values || [];

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Status Updates',
        data: values,
        fill: true,
        borderColor: CHART_COLORS.cyan,
        backgroundColor: 'rgba(6, 182, 212, 0.08)',
        tension: 0.4,
        borderWidth: 2,
        pointBackgroundColor: CHART_COLORS.cyan,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: GRID_COLOR },
          ticks: { color: TEXT_COLOR, font: { family: 'Plus Jakarta Sans' } }
        },
        y: {
          grid: { color: GRID_COLOR },
          ticks: { 
            color: TEXT_COLOR, 
            font: { family: 'Plus Jakarta Sans' },
            stepSize: 1,
            precision: 0
          }
        }
      }
    }
  });
}
