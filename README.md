# StatIQ – Business Reporting & Data Analytics

A Python project that helps analyse business data and generate reports automatically.

I built StatIQ to make the process of analysing sales data and preparing Excel reports easier. Instead of manually calculating everything, users can upload their CSV or Excel files, view important business metrics on a dashboard, and download an automatically generated Excel report.

## What it does

- Upload CSV and Excel files.
- Clean and process the uploaded data.
- Calculate revenue, profit, profit margin, total orders and average order value.
- Display business data through an interactive dashboard.
- Filter data by date, region, product and category.
- Analyse monthly sales, products, regions and categories.
- Generate Excel reports with multiple sheets and charts.
- Apply formatting to the generated Excel reports.

## Built With

- Python
- Pandas
- Streamlit
- OpenPyXL
- Matplotlib

## Project Structure

```text
StatIQ/
│
├── data/
├── reports/
├── app.py
├── sample_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run

**1. Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

**2. Open the project folder**

```bash
cd YOUR_PROJECT_FOLDER
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate it (Windows)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**5. Install the required libraries**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
streamlit run app.py
```

## What's Next?

Some features I'd like to work on in future updates:

- Support for more types of datasets.
- Better data validation and cleaning.
- PDF report generation.
- Automated business insights.
- Sales forecasting.

## About

StatIQ is a project I'm building to improve my Python, data analysis and automation skills while working on something useful for real-world business reporting.