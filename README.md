# FBMessage Explorer - HTML Edition

A web-based tool for exploring and visualizing Facebook Messenger data from HTML exports, adapted from the original [FBMessage](https://github.com/adurivault/FBMessage) project.

## 🎉 Project Status: COMPLETE

This project successfully converts the original FBMessage JavaScript/HTML interface to work with Facebook's HTML export format instead of JSON. All core functionality has been implemented and tested.

### ✅ Features Implemented

- **Interactive Web Interface**: Pure JavaScript/HTML/CSS implementation matching original FBMessage
- **HTML File Processing**: Custom parser for Facebook HTML message exports
- **Real-time Visualizations**: 
  - Scatter plot of messages over time
  - Density charts for date and time distributions
  - Interactive histograms and filters
  - Message browser with hover display
- **Cross-filtering**: Click on any chart to filter all other visualizations
- **Brushing**: Drag to zoom in on specific time periods
- **Modal Dialogs**: Help system and file upload instructions
- **Demo Data**: Loads sample data automatically for testing

### 🔧 Technical Implementation

- **Frontend**: Pure JavaScript using D3.js and Crossfilter.js
- **File Processing**: Custom HTML parser (`html-preprocessing.js`)
- **Server**: Python HTTP server with CORS support (`serve.py`)
- **Data Pipeline**: Converts Facebook HTML structure to original FBMessage format

### 📁 Project Structure

```
FBMess2/
├── index.html                 # Main web interface
├── serve.py                   # HTTP server with CORS
├── js/
│   ├── html-preprocessing.js  # Facebook HTML file parser
│   ├── main.js               # Main application logic
│   ├── barchart.js           # Chart components
│   └── d3.js, crossfilter.js # Visualization libraries
├── css/style.css             # Styling
├── data/demo_messages.json   # Sample data
└── test_*.py                 # Validation scripts
```

### 🚀 Usage

1. **Start the server**:
   ```bash
   cd /home/crispianm/repos/FBMess2
   python serve.py --port 9999
   ```

2. **Open the interface**: http://localhost:9999

3. **Explore demo data**: The interface loads sample data automatically

4. **Upload your data**: 
   - Click "Explore your own data"
   - Download Facebook data in HTML format (not JSON)
   - Select the messages folder in the file picker

### 🧪 Testing Status

All tests pass successfully:
- ✅ File existence validation
- ✅ Demo data loading (21,731 messages)
- ✅ Server accessibility
- ✅ HTML parser with real Facebook data
- ✅ Modal functionality
- ✅ Interactive features

### 📊 Verified Functionality

The following features have been tested and work correctly:

1. **Data Loading**: Both demo and custom HTML file upload
2. **Parsing**: Successful extraction from real Facebook HTML exports
3. **Visualization**: All charts render and update correctly
4. **Interaction**: Filtering, brushing, and cross-filtering work
5. **UI Elements**: Modals, buttons, and file upload function properly

### 🎯 Key Achievements

- **Format Conversion**: Successfully adapted JSON-based processor to HTML format
- **Text Normalization**: Robust handling of Unicode and HTML entities in Facebook data
- **Timestamp Parsing**: Flexible parsing of Facebook's various timestamp formats
- **UI Preservation**: Maintained all original FBMessage interactive features
- **Performance**: Efficient processing of large HTML message archives

### 🔧 Technical Details

**HTML Processing Pipeline**:
1. File selection using regex: `messages/.*message.*\.html`
2. DOM parsing to extract thread titles, participants, and messages
3. Text normalization for Unicode and HTML entities
4. Timestamp parsing with multiple format support
5. Data transformation to match original FBMessage structure

**Browser Compatibility**: 
- Modern browsers with FileReader API support
- Local file access for folder selection
- WebGL for canvas-based scatter plot rendering

## 📝 Documentation

- Full setup instructions in comments
- Inline code documentation
- Test scripts for validation
- User-friendly modal help system

---

**Original FBMessage Authors**: [Mathilde Reynaud](https://github.com/MathReynaud) | [Augustin Durivault](https://github.com/adurivault)  
**HTML Edition**: Crispian Morris

## 🎊 Final Notes

This project successfully demonstrates how to adapt existing data visualization tools to work with different data formats. The HTML edition maintains all the interactive features of the original while adding robust parsing for Facebook's HTML export format.

The interface is production-ready and has been tested with real Facebook data exports containing thousands of messages across multiple conversations.
