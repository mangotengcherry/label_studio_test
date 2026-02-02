# Wafer EDS Labeling Tool

A Streamlit-based tool for labeling Flash Memory Wafer EDS test results.

## Features
- **Data Visualization**: Visualize compressed wafer fail bit maps (130x28 resolution) as density heatmaps.
- **Labeling**: Multi-label support (e.g., Row Fail, Column Fail) using checkboxes.
- **Dynamic Classes**: Add and delete defect classes directly in the UI.
- **Data Management**: Save labels to CSV and download them.
- **Sample Data**: Includes a generator for mock data.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mangotengcherry/label_studio_test.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. (Optional) Generate sample data if `data/` is empty:
   ```bash
   python data_generator.py
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Structure
- `app.py`: Main application.
- `utils.py`: Helper functions for compression and imaging.
- `data_generator.py`: Script to generate mock wafer data.
- `labels.csv`: Stores user labels (auto-generated).
