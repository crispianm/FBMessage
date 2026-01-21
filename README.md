# FBMessage Explorer - HTML & JSON Edition

A web-based tool for exploring and visualizing Facebook Messenger data from HTML or JSON exports, adapted from the original [FBMessage](https://github.com/adurivault/FBMessage) project.

## 🎉 Project Status: ENHANCED

This project successfully converts the original FBMessage JavaScript/HTML interface to work with both Facebook's HTML export format and JSON export format. All core functionality has been implemented and tested with support for both file types.

### ✅ Features Implemented

- **Interactive Web Interface**: Pure JavaScript/HTML/CSS implementation matching original FBMessage
- **Dual Format Support**: 
  - HTML File Processing: Custom parser for Facebook HTML message exports
  - JSON File Processing: Direct parser for Facebook JSON message exports
- **Real-time Visualizations**: 
  - Scatter plot of messages over time
  - Density charts for date and time distributions
  - Interactive histograms and filters
  - Message browser with hover display
- **Cross-filtering**: Click on any chart to filter all other visualizations
- **Brushing**: Drag to zoom in on specific time periods
- **Modal Dialogs**: Help system and file upload instructions
- **Demo Data**: Loads sample data automatically for testing
- **Smart Detection**: Automatically detects whether uploaded files are HTML or JSON format

### 🔧 Technical Implementation

- **Frontend**: Pure JavaScript using D3.js and Crossfilter.js
- **File Processing**: 
  - Custom HTML parser (`html-preprocessing.js`)
  - Custom JSON parser (`json-preprocessing.js`)
  - Unified file handler (`read_files_unified`)
- **Server**: Python HTTP server with CORS support (`serve.py`)
- **Data Pipeline**: Converts both Facebook HTML and JSON structures to original FBMessage format

### 📁 Project Structure

```
FBMessage/
├── index.html                 # Main web interface
├── serve.py                   # HTTP server with CORS
├── js/
│   ├── html-preprocessing.js  # Facebook HTML file parser
│   ├── json-preprocessing.js  # Facebook JSON file parser (NEW)
│   ├── main.js               # Main application logic
│   ├── barchart.js           # Chart components
│   └── d3.js, crossfilter.js # Visualization libraries
├── css/style.css             # Styling
├── data/demo_messages.json   # Sample data
├── test_data/                # Test files for both formats
└── test_*.py                 # Validation scripts
```

### 🚀 Usage

1. **Start the server**:
   ```bash
   cd /home/crispianm/repos/FBMess2
   python serve.py --port 9999
### 🚀 Usage

1. **Start the server**:
   ```bash
   python serve.py
   # or specify a custom port:
   python serve.py -p 8081
   ```

2. **Open the interface**: http://localhost:8080 (or your specified port)

3. **Explore demo data**: The interface loads sample data automatically

4. **Upload your data**: 
   - Click "Explore your own data"
   - Download Facebook data in **either HTML or JSON format**
   - Select the messages folder in the file picker
   - The tool automatically detects and processes the appropriate format

### 📋 Supported File Formats

#### HTML Format
- Traditional Facebook export format
- Files typically named `message_*.html`
- Located in `messages/inbox/` folder structure

#### JSON Format  
- Modern Facebook export format
- Files with `.json` extension
- Each conversation is a separate JSON file
- Example: `"Aidan Johnson_49.json"`

### 🧪 Testing Status

All tests pass successfully:
- ✅ File existence validation
- ✅ Demo data loading (21,731 messages)
- ✅ Server accessibility
- ✅ HTML parser with real Facebook data
- ✅ JSON parser with real Facebook data (NEW)
- ✅ Format auto-detection (NEW)
- ✅ Modal functionality
- ✅ Interactive features

### 📊 Verified Functionality

The following features have been tested and work correctly:

1. **Data Loading**: Demo, custom HTML, and custom JSON file upload
2. **Parsing**: Successful extraction from both HTML and JSON Facebook exports
3. **Auto-Detection**: Smart detection of file format
4. **Visualization**: All charts render and update correctly
5. **Interaction**: Filtering, brushing, and cross-filtering work
6. **UI Elements**: Modals, buttons, and file upload function properly

### 🎯 Key Achievements

- **Dual Format Support**: Successfully supports both HTML and JSON Facebook exports
- **Format Auto-Detection**: Automatically detects and processes the correct format
- **Text Normalization**: Robust handling of Unicode and HTML entities in Facebook data
- **Timestamp Parsing**: Flexible parsing of Facebook's various timestamp formats
- **UI Preservation**: Maintained all original FBMessage interactive features
- **Performance**: Efficient processing of large message archives in both formats

### 🔧 Technical Details

**Processing Pipelines**:

**HTML Processing**:
1. File selection using regex: `messages/.*message.*\.html`
2. DOM parsing to extract thread titles, participants, and messages
3. Text normalization for Unicode and HTML entities
4. Timestamp parsing with multiple format support
5. Data transformation to match original FBMessage structure

**JSON Processing**:
1. File selection using regex: `.*\.json$`
2. Direct JSON parsing to extract thread and message data
3. Support for various JSON message properties (`text`, `content`, media detection)
4. Timestamp conversion from milliseconds to seconds
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
- Support for both HTML and JSON formats

---

**Original FBMessage Authors**: [Mathilde Reynaud](https://github.com/MathReynaud) | [Augustin Durivault](https://github.com/adurivault)  
**HTML & JSON Enhancement**: Crispian Morris
**HTML Edition**: Crispian Morris

## 🎊 Final Notes

This project successfully demonstrates how to adapt existing data visualization tools to work with different data formats. The HTML edition maintains all the interactive features of the original while adding robust parsing for Facebook's HTML export format.

The interface is production-ready and has been tested with real Facebook data exports containing thousands of messages across multiple conversations.
