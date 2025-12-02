# 📋 Anomaly Detector - Project Brief

## 🎯 Project Overview

### Project Name
Anomaly Detector

### Project Goal
Build a standalone web application that automates the detection of abnormal manufacturing test results, allowing non-technical researchers to upload test data files, configure detection criteria, and view highlighted anomalies without manual review.

### Business Context

**Problem:**
Manufacturing quality control generates hundreds of test measurements that currently require manual review to identify unusual results. This is time-consuming and prone to missed anomalies.

**Solution:**
Automated system that flags abnormal test results based on user-defined boundaries, highlighting specific measurements that require researcher investigation.

**Current Status:**
Testing phase - not yet approved by management. Need working prototype to demonstrate value.

---

## 🏗️ Technical Stack

- **Frontend/UI:** Streamlit (Python web framework)
- **Data Processing:** pandas, openpyxl
- **Detection Logic:** Statistical outlier detection (IQR method, expandable to custom boundaries)
- **Storage:** SQLite (for storing user-defined criteria)
- **Visualization:** plotly
- **Package Manager:** uv
- **Deployment:** Streamlit Community Cloud (free hosting)

---

## 📁 Project Structure
```
anomaly-detector/
├── .python-version          # Python 3.11
├── pyproject.toml           # uv dependencies
├── README.md
├── .gitignore
├── app.py                   # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── data_loader.py       # Excel file upload & validation
│   ├── detector.py          # Anomaly detection engine
│   ├── database.py          # SQLite criteria management
│   └── visualizations.py    # Charts and data display
├── tests/
│   ├── test_detector.py
│   └── test_data_loader.py
└── data/
    └── sample_data.xlsx     # Example test data
```

---

## 📊 Data Structure

### Input: Excel File Format

Each Excel file contains manufacturing test results with this hierarchical structure:
```
ITEM_NUMBER (Product/Material)
  └── TEST_NUMBER (Test Session - 28 rows each)
       ├── 5 metadata rows (equipment IDs, conditions)
       ├── 18 measurement rows (9 Dim Stab Warp + 9 Dim Stab Fill replicates)
       ├── 4 summary rows (averages & standard deviations)
       └── 1 completion flag
```

### Key Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ITEM_NUMBER` | string | Product identifier | "WNPZ001100PF" |
| `TEST_NUMBER` | integer | Unique test session ID | 9281558 |
| `RESULT_NAME` | string | Test type/name | "Dim Stab Warp" |
| `RESPONSE` | float | Numerical test result | -3.0 |
| `RESPONSE2` | string | String values (for non-numeric tests) | "Yes" |
| `DATE_TESTED` | string | When test was performed | "11/12/2024 12:32:00 PM" |
| `SAMPLE_NUMBER` | integer | Sample identifier | 5311973 |

### Example Data Rows
```
ITEM_NUMBER: WNPZ001100PF
TEST_NUMBER: 9281558
RESULT_NAME: Dim Stab Warp
RESPONSE: -3.0

ITEM_NUMBER: WNPZ001100PF
TEST_NUMBER: 9281558
RESULT_NAME: Dryer Used
RESPONSE: 759.0
```

### Test Types to Analyze

**Analyze ALL `RESULT_NAME` values EXCEPT these summary fields:**
- ❌ Ave Dim Stab Warp
- ❌ Std Dim Stab Warp
- ❌ Ave Dim Stab Fill
- ❌ Std Dim Stab Fill
- ❌ Test Complete?

**Common test types include:**
- Dim Stab Warp (dimensional stability - warp direction)
- Dim Stab Fill (dimensional stability - fill direction)
- Dryer Used (equipment ID)
- Washer Used (equipment ID)
- Conditioning Time (test condition)
- Wash Conditions (test condition)
- # of Cycles (test parameter)

### Sample Data Statistics

**Example dataset: WNPZ001100PF**
- 27 unique TEST_NUMBERs (test sessions)
- 756 total rows (27 × 28 rows per test)
- 7 test types to analyze (after excluding summary fields)
- 540 measurements analyzed
- 5 abnormal measurements found (0.93%)

---

## 🎯 Core Detection Logic

### Detection Approach

For each `ITEM_NUMBER` + `RESULT_NAME` combination:
1. User defines acceptable range: `[lower_bound, upper_bound]`
2. System flags any `RESPONSE` value outside this range as "ABNORMAL"
3. System categorizes each row as: `NORMAL`, `ABNORMAL`, or `NOT_ANALYZED`

### Example Criteria
```python
# User sets criteria for product WNPZ001100PF:
criteria = {
    'Dim Stab Warp': (-4.75, -2.75),      # Values outside this = ABNORMAL
    'Dim Stab Fill': (-4.125, -1.125),    # Range: [-4.125, -1.125]
    'Dryer Used': (754.0, 762.0),         # Equipment ID range
    'Washer Used': (746.0, 754.0)         # Equipment ID range
}

# Result: A measurement of Dim Stab Warp = -5.0 would be flagged as ABNORMAL
# because -5.0 < -4.75 (below lower bound)
```

### Detection Function Signature
```python
def detect_anomalies(df: pd.DataFrame, item_number: str, criteria: dict) -> pd.DataFrame:
    """
    Detect anomalies in test data based on user-defined boundaries.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input test data (from uploaded Excel file)
    item_number : str
        The specific ITEM_NUMBER to analyze (e.g., 'WNPZ001100PF')
    criteria : dict
        Dictionary mapping RESULT_NAME to (lower_bound, upper_bound)
        Example: {'Dim Stab Warp': (-4.75, -2.75)}
    
    Returns:
    --------
    pd.DataFrame with additional columns:
        - Lower_Bound: Expected lower limit
        - Upper_Bound: Expected upper limit
        - IS_OUTLIER: 'ABNORMAL' or 'NORMAL' or 'NOT_ANALYZED'
    
    Logic:
    ------
    1. Filter df to only rows where ITEM_NUMBER == item_number
    2. For each row:
       - If RESULT_NAME has criteria:
           - If RESPONSE < lower_bound OR RESPONSE > upper_bound:
               IS_OUTLIER = 'ABNORMAL'
           - Else:
               IS_OUTLIER = 'NORMAL'
       - Else:
           IS_OUTLIER = 'NOT_ANALYZED'
    3. Return augmented DataFrame
    """
    pass
```

---

## 🖥️ Application Features

### Page 1: Upload & Configure 📤

**Purpose:** Upload data and set detection criteria

**Components:**

1. **File Upload Widget**
   - Accept Excel files (.xlsx, .xls)
   - Use `st.file_uploader()`
   - Display file preview (first 10 rows using `st.dataframe()`)
   - Show basic stats: total rows, available ITEM_NUMBERs

2. **ITEM_NUMBER Selector**
   - Dropdown (`st.selectbox()`) populated from uploaded file's unique ITEM_NUMBERs
   - Display how many TEST_NUMBERs exist for selected item

3. **RESULT_NAME Filter**
   - Multi-select to choose which test types to analyze
   - Automatically exclude: Ave/Std summary fields and "Test Complete?"
   - Default: select all analyzable tests

4. **Criteria Input Form**
   - For each selected RESULT_NAME, show:
     - Test name
     - Two number inputs: Lower Bound, Upper Bound
     - Current data range (min/max from file) for reference
   - Use `st.data_editor()` for editable table OR
   - Use `st.number_input()` for each bound
   
5. **Action Buttons**
   - "Save Criteria" → stores to SQLite for future use
   - "Load Saved Criteria" → retrieves from SQLite
   - "Run Analysis" → executes detection, shows results

**Example Layout:**
```
┌─────────────────────────────────────────────┐
│  🔍 Anomaly Detector                        │
├─────────────────────────────────────────────┤
│  📤 Upload Test Results                     │
│  [Drag and drop Excel file here]           │
│                                             │
│  ✅ File loaded: test_results.xlsx         │
│  📊 Total rows: 756                         │
│  🏷️  Available products: 13                 │
├─────────────────────────────────────────────┤
│  Select Product:                            │
│  [WNPZ001100PF ▼]                          │
│  27 test sessions found                     │
├─────────────────────────────────────────────┤
│  Configure Detection Criteria:              │
│                                             │
│  Dim Stab Warp                             │
│    Lower: [-4.75] Upper: [-2.75]           │
│    (Current range: -5.0 to -2.75)          │
│                                             │
│  Dim Stab Fill                             │
│    Lower: [-4.125] Upper: [-1.125]         │
│    (Current range: -4.0 to -1.5)           │
│                                             │
│  [Save Criteria] [Load Saved] [Run Analysis]│
└─────────────────────────────────────────────┘
```

---

### Page 2: Analysis Results 📊

**Purpose:** Display detected anomalies with visualizations

**Components:**

1. **Summary Metrics** (4 cards across top)
   - Use `st.metric()` or columns with `st.markdown()`
   - Cards:
```
     [Total Analyzed: 540] [Normal: 535] [Abnormal: 5] [% Abnormal: 0.93%]
```

2. **Affected Test Sessions**
   - List TEST_NUMBERs that have at least one anomaly
   - Show count of anomalies per test
   - Example:
```
     ⚠️ Test Sessions with Anomalies:
     • TEST_NUMBER 9306716: 5 abnormal measurements (Dim Stab Warp)
```

3. **Anomaly Breakdown Chart**
   - Bar chart showing count of anomalies by RESULT_NAME
   - Use Plotly (`plotly.express.bar()`)
   - Interactive tooltips

4. **Detailed Results Table**
   - Show all rows for TEST_NUMBERs with anomalies
   - Columns: TEST_NUMBER, RESULT_NAME, RESPONSE, Lower_Bound, Upper_Bound, IS_OUTLIER
   - **Conditional styling:** 
     - Red background for ABNORMAL rows
     - Use `st.dataframe()` with `styler`
   - Sortable columns
   - Filter options (by RESULT_NAME, IS_OUTLIER)

5. **Export Button**
   - `st.download_button()` to download Excel
   - Apply conditional formatting in Excel output (red cells for ABNORMAL)
   - Include all columns from original data + detection results

**Example Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Analysis Results - WNPZ001100PF                         │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │Total: 540 │ │Normal:535 │ │Abnormal:5 │ │0.93%      │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ⚠️ Affected Test Sessions:                                 │
│  • TEST_NUMBER 9306716 (5 anomalies)                       │
├─────────────────────────────────────────────────────────────┤
│  Anomalies by Test Type:                                    │
│  [Bar Chart: Dim Stab Warp: 5, Others: 0]                 │
├─────────────────────────────────────────────────────────────┤
│  Detailed Anomaly Table:                                    │
│  ┌──────────┬──────────┬─────────┬───────┬───────┬────────┐│
│  │TEST_NUM  │RESULT    │RESPONSE │LOWER  │UPPER  │STATUS  ││
│  ├──────────┼──────────┼─────────┼───────┼───────┼────────┤│
│  │9306716   │Dim Stab W│-5.0     │-4.75  │-2.75  │🔴ABNOR││
│  │9306716   │Dim Stab W│-5.0     │-4.75  │-2.75  │🔴ABNOR││
│  └──────────┴──────────┴─────────┴───────┴───────┴────────┘│
│                                                             │
│  [📥 Download Results as Excel]                            │
└─────────────────────────────────────────────────────────────┘
```

---

### Page 3: Criteria Management ⚙️

**Purpose:** View and manage saved detection criteria

**Components:**

1. **Saved Criteria Table**
   - Display all criteria from database
   - Columns: ITEM_NUMBER, RESULT_NAME, Lower_Bound, Upper_Bound, Created_Date
   - Filter by ITEM_NUMBER
   - Edit/Delete buttons per row
   - Use `st.data_editor()` with callback functions

2. **Import/Export**
   - Export button: Download criteria as JSON file
   - Import widget: Upload JSON file to bulk-add criteria
   - Useful for sharing configurations between users

**Example Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Criteria Management                                     │
├─────────────────────────────────────────────────────────────┤
│  Filter by Product: [All Items ▼]                          │
├─────────────────────────────────────────────────────────────┤
│  Saved Criteria:                                            │
│  ┌──────────┬──────────┬───────┬───────┬──────────┬────────┐│
│  │ITEM      │RESULT    │LOWER  │UPPER  │CREATED   │ACTIONS ││
│  ├──────────┼──────────┼───────┼───────┼──────────┼────────┤│
│  │WNPZ001..│Dim Stab W│-4.75  │-2.75  │2024-11-25│[Edit]..││
│  │WNPZ001..│Dim Stab F│-4.125 │-1.125 │2024-11-25│[Edit]..││
│  └──────────┴──────────┴───────┴───────┴──────────┴────────┘│
│                                                             │
│  [📥 Export Criteria JSON] [📤 Import Criteria JSON]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Database Schema

### Table: anomaly_criteria
```sql
CREATE TABLE anomaly_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_number TEXT NOT NULL,
    result_name TEXT NOT NULL,
    lower_bound REAL NOT NULL,
    upper_bound REAL NOT NULL,
    created_by TEXT DEFAULT 'system',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_number, result_name)
);
```

**Purpose:** Store user-defined detection boundaries for reuse

**Operations:**
- INSERT: Save new criteria
- SELECT: Load criteria for analysis
- UPDATE: Modify existing criteria
- DELETE: Remove criteria

**Example Data:**
```
id | item_number  | result_name    | lower_bound | upper_bound | created_date
1  | WNPZ001100PF | Dim Stab Warp  | -4.75       | -2.75       | 2024-11-25
2  | WNPZ001100PF | Dim Stab Fill  | -4.125      | -1.125      | 2024-11-25
3  | WNPZ001100PF | Dryer Used     | 754.0       | 762.0       | 2024-11-25
```

---

## 🎨 UI/UX Requirements

### Design Principles
- Clean, professional look (Streamlit's default styling is fine)
- Minimal clicks to complete workflow (upload → configure → analyze → export)
- Clear visual indicators (colors, icons)
- Responsive layout
- Loading indicators for operations
- User-friendly error messages

### Color Scheme
- **Normal:** Green (#28a745) or ✅
- **Abnormal:** Red (#dc3545) or ⚠️
- **Not Analyzed:** Gray (#6c757d) or ⚪

### Navigation
- Sidebar with radio buttons or tabs
- Pages: "📤 Upload & Analyze", "📊 Results", "⚙️ Settings"

### Error Handling
- File validation errors: "Invalid file format. Please upload .xlsx or .xls"
- No data errors: "No test data found for ITEM_NUMBER: XXX"
- No criteria errors: "Please set at least one detection criterion"
- Database errors: "Error saving criteria. Please try again."

---

## 🚀 Setup & Deployment

### Initial Setup Commands
```bash
# Create project
uv init anomaly-detector
cd anomaly-detector

# Set Python version
echo "3.11" > .python-version

# Add dependencies
uv add streamlit pandas openpyxl plotly

# Create directory structure
mkdir -p src tests data
touch src/__init__.py
touch src/data_loader.py
touch src/detector.py
touch src/database.py
touch src/visualizations.py
touch app.py

# Initialize git
git init
echo ".venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.db" >> .gitignore
echo "data/*.xlsx" >> .gitignore
```

### Run Locally
```bash
uv run streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to share.streamlit.io
3. Sign in with GitHub
4. Click "New app"
5. Select repository
6. Set main file: `app.py`
7. Deploy (takes ~2 minutes)
8. Share URL: `https://yourapp.streamlit.app`

---

## ✅ Success Criteria

The application must:

1. ✅ Accept Excel file upload with manufacturing test data
2. ✅ Parse Excel and extract ITEM_NUMBER, TEST_NUMBER, RESULT_NAME, RESPONSE columns
3. ✅ Allow users to select ITEM_NUMBER from dropdown
4. ✅ Display available RESULT_NAMEs for selected item
5. ✅ Provide input fields for lower/upper boundaries per test type
6. ✅ Save criteria to SQLite database
7. ✅ Load previously saved criteria
8. ✅ Execute anomaly detection algorithm
9. ✅ Display summary statistics (total, normal, abnormal counts)
10. ✅ Show detailed table with conditional formatting (red for abnormal)
11. ✅ Identify which TEST_NUMBERs have anomalies
12. ✅ Export results to Excel with formatting
13. ✅ Work for non-technical users (no coding knowledge required)
14. ✅ Be shareable via quick easy URL.