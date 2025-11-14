import { useState, useEffect } from 'react';
import './App.css';
import Plot from 'react-plotly.js';

function App() {
  const [data, setData] = useState([]);
  const [reducedFlowsData, setReducedFlowsData] = useState([]);
  const [baseFlowsData, setBaseFlowsData] = useState([]);
  const [junctions, setJunctions] = useState([]);
  const [availabilityJunctions, setAvailabilityJunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJunction, setSelectedJunction] = useState('');
  const [selectedAvailabilityJunction, setSelectedAvailabilityJunction] = useState('');
  const [overviewMode, setOverviewMode] = useState('max'); // 'max' or 'min' or 'avg'
  const [viewMode, setViewMode] = useState('dependable'); // 'dependable' or 'availability'

  // Fullscreen handler
  const handleFullscreen = (elementId) => {
    const element = document.getElementById(elementId);
    if (element) {
      if (element.requestFullscreen) {
        element.requestFullscreen();
      } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
      } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
      }
    }
  };

  useEffect(() => {
    // Load all datasets
    Promise.all([
      fetch('/data.json').then(res => res.json()),
      fetch('/reduced_flows.json').then(res => res.json()),
      fetch('/base_flows.json').then(res => res.json())
    ])
      .then(([dependableData, reducedData, baseData]) => {
        // Set dependable yield data
        setData(dependableData);
        const junctionNames = Object.keys(dependableData[0]).filter(key => key !== 'Date');
        setJunctions(junctionNames);
        setSelectedJunction(junctionNames[0]);
        
        // Set availability data (both reduced and base flows)
        setReducedFlowsData(reducedData);
        setBaseFlowsData(baseData);
        const availJunctionNames = Object.keys(reducedData[0]).filter(key => key !== 'Date');
        setAvailabilityJunctions(availJunctionNames);
        setSelectedAvailabilityJunction(availJunctionNames[0]);
        
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading data:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
  return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading data...</p>
      </div>
    );
  }

  // Prepare data for 75% dependable yield chart
  const singleJunctionData = [{
    x: data.map(d => d.Date),
    y: data.map(d => d[selectedJunction]),
    type: 'scatter',
    mode: 'lines+markers',
    name: selectedJunction,
    line: { color: '#2E86AB', width: 3 },
    marker: {
      size: 6,
      color: '#A23B72',
      line: { color: 'white', width: 1 }
    },
    hovertemplate: '<b>Date:</b> %{x}<br><b>Value:</b> %{y:.4f}<extra></extra>'
  }];

  const singleJunctionLayout = {
    title: {
      text: `75% Dependable Yield - ${selectedJunction}<br><sub>Based on all available years: 1975-2024</sub>`,
      font: { size: 14 }
    },
    xaxis: { 
      title: 'Date (2024)',
      showgrid: true,
      gridcolor: '#E0E0E0',
      automargin: true
    },
    yaxis: { 
      title: '75% Dependable Yield',
      showgrid: true,
      gridcolor: '#E0E0E0',
      rangemode: 'tozero',
      automargin: true
    },
    plot_bgcolor: '#FAFAFA',
    paper_bgcolor: 'white',
    hovermode: 'x unified',
    height: 600,
    font: { size: 12 },
    autosize: true
  };

  // Prepare data for all junctions overview
  const getColorForMode = () => {
    if (overviewMode === 'max') return '#2E86AB';
    if (overviewMode === 'min') return '#A23B72';
    return '#F18F01';
  };

  const getModeLabel = () => {
    if (overviewMode === 'max') return 'Maximum';
    if (overviewMode === 'min') return 'Minimum';
    return 'Average';
  };

  const overviewValues = junctions.map(junction => {
    const values = data.map(d => d[junction]).filter(v => v != null);
    if (overviewMode === 'max') {
      return Math.max(...values);
    } else if (overviewMode === 'min') {
      return Math.min(...values);
    } else {
      return values.reduce((sum, val) => sum + val, 0) / values.length;
    }
  });

  const allJunctionsData = [{
    x: junctions,
    y: overviewValues,
    type: 'bar',
    marker: {
      color: getColorForMode(),
      line: {
        color: 'white',
        width: 1
      }
    },
    hovertemplate: '<b>%{x}</b><br><b>' + getModeLabel() + ':</b> %{y:.4f}<extra></extra>'
  }];

  const allJunctionsLayout = {
    title: {
      text: `75% Dependable Yield - All Junctions (${getModeLabel()} Values)<br><sub>Based on all available years: 1975-2024</sub>`,
      font: { size: 14 }
    },
    xaxis: { 
      title: 'Junction Name',
      showgrid: false,
      tickangle: -45,
      tickfont: { size: 10 },
      automargin: true
    },
    yaxis: { 
      title: `${getModeLabel()} 75% Dependable Yield`,
      showgrid: true,
      gridcolor: '#E0E0E0',
      rangemode: 'tozero',
      automargin: true
    },
    plot_bgcolor: '#FAFAFA',
    paper_bgcolor: 'white',
    height: 650,
    font: { size: 11 },
    showlegend: false,
    margin: {
      l: 80,
      r: 50,
      t: 100,
      b: 180
    },
    autosize: true
  };

  // Prepare data for availability chart (with stacked bars and lines)
  const maxPickup = 3.0;
  
  // Calculate Y-axis max for CURRENT junction only (auto-scale like Python chart)
  const currentMaxReduced = Math.max(
    ...reducedFlowsData.map(d => Math.max(d[selectedAvailabilityJunction] || 0, 0))
  );
  const currentMaxBase = Math.max(
    ...baseFlowsData.map(d => Math.max(d[selectedAvailabilityJunction] || 0, 0))
  );
  const currentMax = Math.max(currentMaxReduced, currentMaxBase, maxPickup);
  const yAxisMax = currentMax + 0.5; // Add small padding
  
  // Define ranges and colors (REVERSED: light blue at bottom, dark blue at top)
  const colorRanges = [
    { start: 0.0, end: 0.5, color: '#ADD8E6', name: '0.0-0.5' },   // Light Blue (bottom)
    { start: 0.5, end: 1.0, color: '#87CEEB', name: '0.5-1.0' },   // Sky Blue
    { start: 1.0, end: 1.5, color: '#1E90FF', name: '1.0-1.5' },   // Dodger Blue
    { start: 1.5, end: 2.0, color: '#4169E1', name: '1.5-2.0' },   // Royal Blue
    { start: 2.0, end: 2.5, color: '#0000CD', name: '2.0-2.5' },   // Medium Blue
    { start: 2.5, end: 3.0, color: '#00008B', name: '2.5-3.0' },   // Dark Blue (top)
  ];
  
  // Create stacked bars for each range
  const availabilityChartData = colorRanges.map(range => {
    const yValues = reducedFlowsData.map(d => {
      // Ensure value is at least 0 (no negatives)
      const rawValue = d[selectedAvailabilityJunction] || 0;
      const value = Math.min(Math.max(rawValue, 0), maxPickup);
      if (value > range.start) {
        return Math.min(value - range.start, range.end - range.start);
      }
      return 0;
    });
    
    return {
      x: reducedFlowsData.map(d => d.Date),
      y: yValues,
      type: 'bar',
      name: `${range.name} MCM`,  // Show range in legend
      marker: { 
        color: range.color,
        line: {
          width: 0
        }
      },
      showlegend: true,  // Show in legend
      hoverinfo: 'skip',
      legendgroup: 'bars'  // Group all bars together
    };
  });
  
  // Add the lines on top of bars
  availabilityChartData.push(
    // Maximum Pickup line (add first so it's behind other lines)
    {
      x: reducedFlowsData.map(d => d.Date),
      y: reducedFlowsData.map(() => maxPickup),
      type: 'scatter',
      mode: 'lines',
      name: 'Maximum Pickup',
      line: { color: '#FF6F00', width: 3 },
      hovertemplate: '<b>Maximum Pickup:</b> 3.0 MCM<extra></extra>'
    },
    // Base Flows Line (Orange - plot first)
    {
      x: baseFlowsData.map(d => d.Date),
      y: baseFlowsData.map(d => {
        const val = d[selectedAvailabilityJunction];
        return (val !== null && val !== undefined && !isNaN(val)) ? Math.max(val, 0) : 0;
      }),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Base Flows',
      line: { color: '#F57C00', width: 3 },
      marker: {
        size: 6,
        color: '#F57C00',
        symbol: 'square',
        line: { color: 'white', width: 1 }
      },
      hovertemplate: '<b>Date:</b> %{x}<br><b>Base Flows:</b> %{y:.2f} MCM<extra></extra>',
      connectgaps: false,
      yaxis: 'y'
    },
    // Reduced Flows Line (Blue - plot second so it's on top)
    {
      x: reducedFlowsData.map(d => d.Date),
      y: reducedFlowsData.map(d => {
        const val = d[selectedAvailabilityJunction];
        return (val !== null && val !== undefined && !isNaN(val)) ? Math.max(val, 0) : 0;
      }),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Reduced Flows',
      line: { color: '#0D47A1', width: 3 },
      marker: {
        size: 6,
        color: '#0D47A1',
        symbol: 'circle',
        line: { color: 'white', width: 1 }
      },
      hovertemplate: '<b>Date:</b> %{x}<br><b>Reduced Flows:</b> %{y:.2f} MCM<extra></extra>',
      connectgaps: false,
      yaxis: 'y'
    }
  );

  // No annotations - clean bars without text
  const annotations = [];

  const availabilityLayout = {
    title: {
      text: selectedAvailabilityJunction,
      font: { size: 16, weight: 'bold' },
      x: 0.5,
      xanchor: 'center'
    },
    xaxis: { 
      title: 'Date',
      showgrid: true,
      gridcolor: '#d3d3d3',
      gridwidth: 0.5,
      automargin: true,
      tickangle: -90,
      tickfont: { size: 9 }
    },
    yaxis: { 
      title: 'Availability',
      showgrid: true,
      gridcolor: '#d3d3d3',
      gridwidth: 0.5,
      tick0: 0,
      dtick: 0.5,  // Show every 0.5 like Python chart
      rangemode: 'tozero',
      range: [0, yAxisMax],
      automargin: true,
      tickfont: { size: 10 },
      tickformat: '.1f'  // Format as decimal (0.0, 0.5, 1.0, 1.5...)
    },
    plot_bgcolor: '#fafafa',
    paper_bgcolor: 'white',
    hovermode: 'x unified',
    height: 650,
    font: { size: 12 },
    barmode: 'stack',
    bargap: 0,
    bargroupgap: 0,
    barnorm: '',
    annotations: annotations,
    legend: {
      orientation: 'v',  // Vertical legend on right
      yanchor: 'top',
      y: 0.98,
      xanchor: 'left',
      x: 1.01,  // Position to the right
      bgcolor: 'rgba(255, 255, 255, 0.95)',
      bordercolor: '#e5e7eb',
      borderwidth: 1,
      font: { size: 10 },
      title: {
        text: '<b>Legend</b>',
        font: { size: 11 }
      }
    },
    autosize: true
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1>Water Junction Dashboard</h1>
            <p>75% Dependable Yield & Availability Analysis (1975-2024)</p>
          </div>
          
          {/* View Mode Selector in Header */}
          <div className="view-mode-selector">
            <button 
              className={viewMode === 'dependable' ? 'active' : ''}
              onClick={() => setViewMode('dependable')}
            >
              75% Dependable Yield
            </button>
            <button 
              className={viewMode === 'availability' ? 'active' : ''}
              onClick={() => setViewMode('availability')}
            >
              Availability Charts
        </button>
          </div>
        </div>
      </header>

      <div className="main-container">
        <div className="content">

          {viewMode === 'dependable' ? (
            <>
              {/* 75% Dependable Yield Charts */}
              <section className="chart-section">
                <div className="section-header">
                  <h2>Individual Junction - 75% Dependable Yield</h2>
                  <div className="header-controls">
                    <select 
                      value={selectedJunction} 
                      onChange={(e) => setSelectedJunction(e.target.value)}
                      className="junction-select"
                    >
                      {junctions.map(junction => (
                        <option key={junction} value={junction}>{junction}</option>
                      ))}
                    </select>
                    <button 
                      className="fullscreen-btn"
                      onClick={() => handleFullscreen('chart1')}
                      title="Fullscreen"
                    >
                      ⛶
                    </button>
                  </div>
                </div>
                <div className="chart-wrapper" id="chart1">
                  <Plot
                    data={singleJunctionData}
                    layout={singleJunctionLayout}
                    config={{ 
                      responsive: true, 
                      displayModeBar: true,
                      modeBarButtonsToAdd: ['toImage'],
                      displaylogo: false,
                      toImageButtonOptions: {
                        format: 'png',
                        filename: `${selectedJunction}_dependable_yield`,
                        height: 800,
                        width: 1400,
                        scale: 2
                      }
                    }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </section>

              <section className="chart-section">
                <div className="section-header">
                  <h2>All Junctions Overview</h2>
                  <div className="header-controls">
                    <select 
                      value={overviewMode} 
                      onChange={(e) => setOverviewMode(e.target.value)}
                      className="junction-select"
                    >
                      <option value="max">Maximum Values</option>
                      <option value="min">Minimum Values</option>
                      <option value="avg">Average Values</option>
                    </select>
                    <button 
                      className="fullscreen-btn"
                      onClick={() => handleFullscreen('chart2')}
                      title="Fullscreen"
                    >
                      ⛶
                    </button>
                  </div>
                </div>
                <div className="chart-wrapper" id="chart2">
                  <Plot
                    data={allJunctionsData}
                    layout={allJunctionsLayout}
                    config={{ 
                      responsive: true, 
                      displayModeBar: true,
                      modeBarButtonsToAdd: ['toImage'],
                      displaylogo: false,
                      toImageButtonOptions: {
                        format: 'png',
                        filename: `all_junctions_${overviewMode}`,
                        height: 800,
                        width: 1400,
                        scale: 2
                      }
                    }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </section>
            </>
          ) : (
            <>
              {/* Availability Charts - Plotly HTML Embeds */}
              <section className="chart-section">
                <div className="section-header">
                  <h2>Junction Availability Analysis - Threshold Charts</h2>
                  <div className="header-controls">
                    <select 
                      value={selectedAvailabilityJunction} 
                      onChange={(e) => setSelectedAvailabilityJunction(e.target.value)}
                      className="junction-select"
                    >
                      {availabilityJunctions.map(junction => (
                        <option key={junction} value={junction}>{junction}</option>
                      ))}
                    </select>
                    <button 
                      className="fullscreen-btn"
                      onClick={() => handleFullscreen('chart3')}
                      title="Fullscreen"
                    >
                      ⛶
                    </button>
                  </div>
                </div>
                <div className="chart-wrapper-iframe" id="chart3">
                  <iframe 
                    src={`/availability_charts/${selectedAvailabilityJunction}_plotly.html`}
                    title={`${selectedAvailabilityJunction} Availability Chart`}
                    style={{ 
                      width: '100%', 
                      height: '800px', 
                      border: 'none',
                      borderRadius: '8px',
                      display: 'block'
                    }}
                  />
                </div>
                <div className="info-box">
                  <p><strong>Chart Features:</strong> Interactive threshold-based availability analysis showing:
                  </p>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    <li><strong>Horizontal Bars:</strong> Color-coded capacity thresholds (0-3.0 MCM)</li>
                    <li><strong>Blue Line:</strong> Reduced Flows (with circle markers)</li>
                    <li><strong>Orange Dashed Line:</strong> Base Flows (with square markers)</li>
                    <li><strong>Orange Solid Line:</strong> Maximum Pickup threshold (3.0 MCM)</li>
                    <li><strong>Legend Table:</strong> Capacity ranges with days and period (First/Mid/Last month)</li>
                  </ul>
                </div>
              </section>
            </>
          )}
        </div>
      </div>

      <footer className="app-footer">
        <p>Data Period: 1975-2024 | Total Junctions: {junctions.length}</p>
      </footer>
    </div>
  );
}

export default App;
