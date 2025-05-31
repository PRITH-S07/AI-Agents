# Scotty Scheduler


## Data Resources
- `syllabi_pdfs_fall2024ECE.zip`: Fall 2024 ECE course syllabi
- `syllabi_pdfs_spring2025ECE.zip`: Spring 2025 ECE course syllabi

## Getting Started

### Prerequisites
- Python 3.x
- Required Python packages (to be added to requirements.txt)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/PRITH-S07/Scotty-Scheduler.git
cd Scotty-Scheduler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Extract the required data files:
- Unzip `syllabi_pdfs_fall2024ECE.zip` and `syllabi_pdfs_spring2025ECE.zip` in the data directory
- Extract `stored_index.zip` for pre-processed data

### Usage
1. Run the main application:
```bash
python home.py
```

2. For inference testing:
```bash
python inference.py
```

## Components

### Syllabus Scraper
The `syllabus_scraper.py` tool extracts relevant information from course syllabi PDFs.

### Inference System
The inference system (`inference.py`) processes course data and generates optimized schedules.

### Data Processing
- Raw data is stored in the `data/` directory
- Processed data is available in `cleaned_data/`
