import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
from utils import compress_wafer_map, generate_heatmap_image
from datetime import datetime

# Configuration
DATA_DIR = "data"
LABELS_FILE = "labels.csv"
CLASSES = ["Normal", "Row Fail", "Column Fail", "Cluster Fail", "Big Fail", "Edge Fail", "Unknown"]

st.set_page_config(layout="wide", page_title="Wafer EDS Labeling Tool")

# --- Helper Functions ---
def load_labels():
    if os.path.exists(LABELS_FILE):
        df = pd.read_csv(LABELS_FILE, index_col=0)
        # Fix: Drop "filename" column if it accidentally got saved as a column (due to previous bug)
        if "filename" in df.columns:
            df = df.drop(columns=["filename"])
        return df
    else:
        # Fix: Initialize without "filename" in columns, since it will be the index
        df = pd.DataFrame(columns=["label", "labeled_at"])
        df.index.name = "filename"
        return df

def save_label(filename, label):
    df = load_labels()
    
    # Update or Append
    if filename in df.index:
        df.at[filename, "label"] = label
        df.at[filename, "labeled_at"] = datetime.now().isoformat()
    else:
        new_row = pd.DataFrame({"label": [label], "labeled_at": [datetime.now().isoformat()]})
        new_row.index = [filename]
        new_row.index.name = "filename"
        df = pd.concat([df, new_row])
    
    df.to_csv(LABELS_FILE)
    return df

def get_files():
    files = glob.glob(os.path.join(DATA_DIR, "*.npy"))
    files = [os.path.basename(f) for f in files]
    # Human numeric sort if possible, otherwise standard sort
    files.sort()
    return files

# --- State Management ---
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Initialize Classes if not already in session state
if "classes" not in st.session_state:
    st.session_state.classes = ["Normal", "Row Fail", "Column Fail", "Cluster Fail", "Big Fail", "Edge Fail", "Unknown"]

files = get_files()
if not files:
    st.error("No .npy files found in 'data/' directory. Please run data_generator.py first.")
    st.stop()

# --- CSS Styling (Label Studio feel) ---
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: bold; color: #333; margin-bottom: 1rem; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .viewer-container { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("Wafer Labeler")
st.sidebar.markdown("---")

# Navigation
if st.sidebar.button("Previous") and st.session_state.current_index > 0:
    st.session_state.current_index -= 1
    st.rerun()

if st.sidebar.button("Next") and st.session_state.current_index < len(files) - 1:
    st.session_state.current_index += 1
    st.rerun()

# File List
selected_file = st.sidebar.selectbox(
    "Select Wafer", 
    files, 
    index=st.session_state.current_index
)
# Sync selection with index if User specifically picks from dropdown
if selected_file != files[st.session_state.current_index]:
    st.session_state.current_index = files.index(selected_file)
    st.rerun()

# Stats
labels_df = load_labels()
labeled_count = len(labels_df)
progress = labeled_count / len(files)
st.sidebar.progress(progress)
st.sidebar.write(f"Progress: {labeled_count} / {len(files)}")

st.sidebar.markdown("---")
# Download
csv = labels_df.to_csv().encode('utf-8')
st.sidebar.download_button(
    label="Download Labels CSV",
    data=csv,
    file_name='wafer_labels.csv',
    mime='text/csv',
)


# --- Main Area ---
st.markdown(f"<div class='main-header'>Labeling: {selected_file}</div>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    # Load and Process Data
    file_path = os.path.join(DATA_DIR, selected_file)
    try:
        raw_data = np.load(file_path)
        
        # Compression
        compressed_map = compress_wafer_map(raw_data)
        
        # Heatmap
        img = generate_heatmap_image(compressed_map)
        
        # Display (Upscale for visibility)
        st.markdown("<div class='viewer-container'>", unsafe_allow_html=True)
        # Fix: use_container_width -> use_column_width for compatibility
        st.image(img, caption=f"Density Map (Max: {np.max(compressed_map)} fails/block)", use_column_width=True) 
        st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading file: {e}")

with col2:
    # Check if already labeled
    current_label_str = labels_df.loc[selected_file, "label"] if selected_file in labels_df.index else ""
    # Parse potential multi-labels (comma separated)
    current_labels = [l.strip() for l in str(current_label_str).split(",")] if current_label_str and str(current_label_str) != "nan" else []
    
    # Ensure current label is in our list if it exists (e.g. from file)
    for label in current_labels:
        if label and label not in st.session_state.classes:
            st.session_state.classes.append(label)
        
    # Form for labeling
    with st.form("label_form"):
        st.write("Defect Types (Multi-select)")
        
        # Use Checkboxes for multi-selection
        selected_classes = []
        for cls in st.session_state.classes:
            # Check if this class is currently active for this file
            is_checked = cls in current_labels
            if st.checkbox(cls, value=is_checked):
                selected_classes.append(cls)
        
        st.markdown("---")
        # "Save" button effectively
        submitted = st.form_submit_button("Save & Next", type="primary")
        
        if submitted:
            # Join multiple labels with comma
            label_string = ", ".join(selected_classes)
            save_label(selected_file, label_string)
            st.success(f"Saved: {label_string}")
            
            # Auto advance
            if st.session_state.current_index < len(files) - 1:
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.info("Finished all files!")
    
    st.markdown("---")
    st.subheader("Class Management")
    
    # Add new class
    col_add, col_del = st.columns(2)
    with col_add:
        new_class = st.text_input("New Class Name", key="new_class_input")
        if st.button("Add"):
            if new_class and new_class not in st.session_state.classes:
                st.session_state.classes.append(new_class)
                st.success(f"Added {new_class}")
                st.rerun()
    
    with col_del:
        class_to_del = st.selectbox("Delete Class", [""] + st.session_state.classes, key="del_class_select")
        if st.button("Delete"):
            if class_to_del and class_to_del in st.session_state.classes:
                st.session_state.classes.remove(class_to_del)
                st.warning(f"Deleted {class_to_del}")
                st.rerun()

# --- Data Preview ---
st.markdown("---")
st.subheader("Label Data Preview")
# Removed use_column_width/use_container_width to be safe across versions
st.dataframe(load_labels())
