import { useState, useEffect } from 'react';
import './App.css';
import Plot from 'react-plotly.js';

function App() {
  const [data, setData] = useState([]);
  const [junctions, setJunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJunction, setSelectedJunction] = useState('');
  const [overviewMode, setOverviewMode] = useState('max'); // 'max' or 'min'

  useEffect(() => {
    // Load data from JSON file
    fetch('/data.json')
      .then(response => response.json())
      .then(jsonData => {
        setData(jsonData);
        // Extract junction names (all columns except 'Date')
        const junctionNames = Object.keys(jsonData[0]).filter(key => key !== 'Date');
        setJunctions(junctionNames);
        setSelectedJunction(junctionNames[0]);
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
        <p>Loading charts...</p>
      </div>
    );
  }

  // Prepare data for selected junction chart
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
    title: `75% Dependable Yield - ${selectedJunction}<br><sub>Based on all available years: 1975-2024</sub>`,
    xaxis: { 
      title: 'Date (2024)',
      showgrid: true,
      gridcolor: '#E0E0E0'
    },
    yaxis: { 
      title: '75% Dependable Yield',
      showgrid: true,
      gridcolor: '#E0E0E0'
    },
    plot_bgcolor: '#FAFAFA',
    paper_bgcolor: 'white',
    hovermode: 'x unified',
    height: 600,
    font: { size: 12 }
  };

  // Prepare data for all junctions overview (bar chart with max/min/average values)
  const overviewValues = junctions.map(junction => {
    const values = data.map(d => d[junction]).filter(v => v != null);
    if (overviewMode === 'max') {
      return Math.max(...values);
    } else if (overviewMode === 'min') {
      return Math.min(...values);
    } else { // average
      return values.reduce((sum, val) => sum + val, 0) / values.length;
    }
  });

  // Determine color and label based on mode
  const getColorForMode = () => {
    if (overviewMode === 'max') return '#2E86AB'; // Blue
    if (overviewMode === 'min') return '#A23B72'; // Purple
    return '#F18F01'; // Orange for average
  };

  const getModeLabel = () => {
    if (overviewMode === 'max') return 'Maximum';
    if (overviewMode === 'min') return 'Minimum';
    return 'Average';
  };

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
    title: `75% Dependable Yield - All Junctions (${getModeLabel()} Values)<br><sub>Based on all available years: 1975-2024</sub>`,
    xaxis: { 
      title: 'Junction Name',
      showgrid: false,
      tickangle: -45
    },
    yaxis: { 
      title: `${getModeLabel()} 75% Dependable Yield`,
      showgrid: true,
      gridcolor: '#E0E0E0'
    },
    plot_bgcolor: '#FAFAFA',
    paper_bgcolor: 'white',
    height: 600,
    font: { size: 11 },
    showlegend: false,
    margin: {
      b: 150 // Extra bottom margin for rotated labels
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📊 75% Dependable Yield Charts</h1>
        <p>Interactive visualization of water junction yield data (1975-2024)</p>
      </header>

      <div className="main-container">
        <div className="content">
          {/* Individual Junction Chart */}
          <section className="chart-section">
            <div className="section-header">
              <h2>Individual Junction Chart</h2>
              <select 
                value={selectedJunction} 
                onChange={(e) => setSelectedJunction(e.target.value)}
                className="junction-select"
              >
                {junctions.map(junction => (
                  <option key={junction} value={junction}>{junction}</option>
                ))}
              </select>
            </div>
            <div className="chart-wrapper">
              <Plot
                data={singleJunctionData}
                layout={singleJunctionLayout}
                config={{ responsive: true, displayModeBar: true }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </section>

          {/* All Junctions Chart */}
          <section className="chart-section">
            <div className="section-header">
              <h2>All Junctions Overview</h2>
              <select 
                value={overviewMode} 
                onChange={(e) => setOverviewMode(e.target.value)}
                className="junction-select"
              >
                <option value="max">Maximum Values</option>
                <option value="min">Minimum Values</option>
                <option value="avg">Average Values</option>
              </select>
            </div>
            <div className="chart-wrapper">
              <Plot
                data={allJunctionsData}
                layout={allJunctionsLayout}
                config={{ responsive: true, displayModeBar: true }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </section>
        </div>
      </div>

      <footer className="app-footer">
        <p>Data Period: 1975-2024 | Total Junctions: {junctions.length}</p>
      </footer>
    </div>
  );
}

export default App;
