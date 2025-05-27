# PID Regulation Verifier

A compliance analysis tool that verifies whether a P&ID (Piping and Instrumentation Diagram) matches the requirements outlined in an SOP (Standard Operating Procedure). It extracts components from the diagram using a YOLOv8 object detection model and parses regulatory logic from Word-based SOP files, then compares the two and logs discrepancies.

---

## Features

- Parses SOP `.docx` documents for stepwise regulatory component requirements
- Uses YOLOv8 and OpenCV for component detection on engineering diagrams (P&ID)
- Builds a graph representation of the process network from detected components using NetworkX
- Detects missing components by comparing with the Standard Operating Procedure and logs discrepancies with timestamps and severity
- Generates a structured Markdown report and graph representing the given P&ID diagram for easy review

---

## Installation

  1. Clone the repo
  ```bash
  git clone https://github.com/Rohan-dev-C/PID-Regulation-Verifier.git
  cd PID-Regulation-Verifier
  ```
  2. Set up Python environment
  ```bash
  conda create -n pid-verifier python=3.12 -y
  conda activate pid-verifier
  ```



