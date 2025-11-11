# 75% Dependable Yield Charts - React

A simple, interactive React web application for visualizing water junction yield data.

## 🚀 Features

### 📊 Two Interactive Charts

1. **Individual Junction Chart**
   - Dropdown selector to choose any junction
   - Interactive Plotly chart with zoom, pan, and hover
   - Detailed view of single junction data

2. **All Junctions Overview**
   - All junctions displayed on one chart
   - Color-coded lines for each junction
   - Legend to show/hide specific junctions

### 🎯 Interactive Features
- **Zoom & Pan** - Click and drag to zoom, double-click to reset
- **Hover Tooltips** - See exact values on hover
- **Legend Toggle** - Click legend items to show/hide junctions
- **Download Charts** - Camera icon to save as PNG

## 📦 Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Ensure data exists:**
The `public/data.json` file contains the junction data.

## 🏃‍♂️ Running the Application

Start the development server:

```bash
npm run dev
```

The application will open at `http://localhost:5173`

## 📁 Project Structure

```
junction-dashboard/
├── public/
│   └── data.json          # Water junction data
├── src/
│   ├── App.jsx            # Main application (all charts)
│   ├── App.css            # Styles
│   └── main.jsx           # Entry point
└── package.json
```

## 🎨 Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Plotly.js** - Interactive charting library

## 💡 Usage

1. **Individual Junction Chart:**
   - Select a junction from the dropdown
   - Interact with the chart (zoom, pan, hover)

2. **All Junctions Chart:**
   - View all junctions at once
   - Click legend items to show/hide specific junctions
   - Hover to see values

## 📊 Data Format

The `public/data.json` file should have this structure:

```json
[
  {
    "Date": "01-Jan",
    "Junction1": 123.45,
    "Junction2": 234.56,
    ...
  },
  ...
]
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🌐 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

---

**Note:** Use the Python scripts in the parent directory to process Excel data and generate the JSON file.
