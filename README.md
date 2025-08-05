CSV Filter Tool - Streamlit + FastAPI
Overview
This application provides a powerful CSV filtering solution that combines Streamlit's user-friendly interface with a FastAPI backend for handling large files. The system automatically determines whether to process files locally (for small files <200MB) or send them to a cloud backend (for larger files).

Features
Dual Processing Mode:

Small files (<200MB) processed directly in Streamlit

Large files automatically sent to FastAPI backend

Advanced Filtering:

Multiple filter conditions

Exact or contains matching

Regex support

Wildcard support (*)

Preview & Download:

View filtered results preview

Download full filtered dataset
