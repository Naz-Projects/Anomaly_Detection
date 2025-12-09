# Anomaly Detector

**A simple tool to automatically find unusual test results in manufacturing data.**

---

## What Does This Tool Do?

This tool helps you quickly identify abnormal measurements in manufacturing test data without having to manually review hundreds of rows in Excel.

---

## How to Use the Tool

### Step 1: Open the Application

Click on your deployment link (e.g., `https://anomalydetection-naz.streamlit.app/`)

### Step 2: Upload Your Excel File

1. Click the **"Choose an Excel file"** button
2. Select your test results file (must be `.xlsx` or `.xls` format)
3. The tool will show you:
   - Total number of rows in your file
   - Number of different products
   - Number of test sessions

### Step 3: Select Products to Analyze

- By default, **all products** in your file are selected
- To analyze specific products only:
  - Click the X next to any product name to remove it
  - Or clear all and select only the ones you want

### Step 4: Add Filters (Detection Criteria)

Filters tell the tool what's considered "normal" vs "abnormal" for each test measurement.

1. Click the **"➕ Add Filter"** button
2. For each filter:
   - **Select Test Type**: Choose which measurement to monitor (e.g., "Dim Stab Warp")
   - **Set Lower Bound**: Enter the minimum acceptable value
   - **Set Upper Bound**: Enter the maximum acceptable value
   - The tool shows the current data range to help you decide

**Example Filter:**
- Test Type: Dim Stab Warp
- Lower Bound: -4.75
- Upper Bound: -2.75
- Result: Any value below -4.75 or above -2.75 will be flagged as ABNORMAL

3. Add as many filters as needed for different test types
4. To remove a filter, click the **✕** button next to it

### Step 5: Run the Analysis

1. Click the **"▶ Run Analysis"** button
2. Wait a few seconds while the tool processes your data
3. Results appear below!

---

## Understanding Your Results

### Summary Metrics

At the top, you'll see three numbers:

- **Total Analyzed**: How many measurements were checked
- **Normal**: How many measurements are within acceptable ranges
- **Abnormal**: How many measurements fall outside acceptable ranges ⚠️

### Detailed Anomaly Records

A table showing **only the abnormal measurements** with:

- **ITEM_NUMBER**: Which product
- **TEST_NUMBER**: Which test session
- **RESULT_NAME**: Which measurement type
- **RESPONSE**: The actual value that was measured
- **Lower_Bound**: What you set as the minimum acceptable value
- **Upper_Bound**: What you set as the maximum acceptable value
- **IS_OUTLIER**: Will show "ABNORMAL" for flagged items

### Download Results

Click **"Download Results (Excel with highlighting)"** to get:
- A complete Excel file with all your data
- Abnormal rows highlighted in **light red** for easy review
- All columns from your original data plus the analysis results

---

## Important Notes

### What Data Gets Analyzed?

✅ **Analyzed:**
- All test measurements (Dim Stab Warp, Dim Stab Fill, equipment IDs, etc.)

❌ **NOT Analyzed (automatically excluded):**
- Ave Dim Stab Warp
- Std Dim Stab Warp
- Ave Dim Stab Fill
- Std Dim Stab Fill
- Test Complete?

These are summary fields and don't need anomaly detection.

### What Does "Normal" Mean?

- If you add filters, measurements within your specified bounds = NORMAL
- Measurements outside your bounds = ABNORMAL
- All other measurements (without filters) = NORMAL by default

### Required Excel Format

Your Excel file must have these columns:
- `ITEM_NUMBER` - Product/material identifier
- `TEST_NUMBER` - Test session ID
- `RESULT_NAME` - Type of measurement
- `RESPONSE` - The measured value

---

## Example Workflow

**Scenario:** You want to check dimensional stability tests for fabric product "WNPZ001100PF"

1. **Upload** your test results Excel file
2. **Select** only product "WNPZ001100PF" (or keep all products selected)
3. **Add Filter #1:**
   - Test Type: Dim Stab Warp
   - Lower: -4.75
   - Upper: -2.75
4. **Add Filter #2:**
   - Test Type: Dim Stab Fill
   - Lower: -4.125
   - Upper: -1.125
5. **Click** "Run Analysis"
6. **Review** the results - any measurements outside these ranges are flagged
7. **Download** the Excel file with highlighted abnormal rows
8. **Investigate** the flagged test sessions

---

## Tips for Best Results

1. **Look at the data range** shown under each filter to help set realistic bounds
2. **Start with fewer filters** to get familiar with the tool
3. **Download results** to share with your team or keep records
4. **Re-run analysis** anytime by adjusting your filters and clicking "Run Analysis" again
5. **Clear Results** button lets you start fresh with new filters

---

## Need Help?

If you encounter any issues or have questions about using the tool, please contact your IT support or the person who deployed this application.

---

## Technical Information (For IT/Developers)

**Deployment:** Streamlit Community Cloud
**Repository:** https://github.com/gorefabrics/Anomaly_Detector
**Requirements:** Python 3.11+, Streamlit, pandas, openpyxl, plotly

For technical documentation or to modify the tool, see the repository README or contact the development team.
