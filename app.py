
from pathlib import Path

import pandas as pd
import streamlit as st



# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "unit_cost"
]

OPTIONAL_COLUMNS = [
    "category",
    "region",
    "sales_rep",
    "customer"
]


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------


def load_file(uploaded_file):

    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "csv":

        try:
            df = pd.read_csv(
                uploaded_file,
                encoding="utf-8-sig"
            )

        except UnicodeDecodeError:
            uploaded_file.seek(0)

            try:
                df = pd.read_csv(
                    uploaded_file,
                    encoding="cp1252"
                )

            except UnicodeDecodeError:
                uploaded_file.seek(0)

                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin1"
                )

    elif file_extension == "xlsx":

        df = pd.read_excel(
            uploaded_file,
            engine="openpyxl"
        )

    else:
        raise ValueError(
            "Unsupported file format. Upload CSV or XLSX."
        )

    return df




# --------------------------------------------------
# 3. CLEAN AND VALIDATE DATA
# --------------------------------------------------

def clean_data(df):

    original_rows = len(df)

    # Standardize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )


    # Automatically recognise different column names
    column_aliases = {
        "order_id": ["order id", "order number", "orderid"],
        "order_date": ["order date", "date", "purchase date"],
        "product": ["product name", "item", "item name"],
        "quantity": ["qty", "units", "units sold"],
        "unit_price": ["price", "selling price"],
        "unit_cost": ["cost", "cost price"],
        "category": ["product category"],
        "region": ["sales region", "area"],
        "sales_rep": ["salesperson", "sales person", "representative"],
        "customer": ["customer name", "client"]
    }

    # Rename recognised columns
    for standard_name, aliases in column_aliases.items():
        if standard_name not in df.columns:
            for alias in aliases:
                normalized_alias = alias.replace(" ", "_")

                if normalized_alias in df.columns:
                    df = df.rename(
                        columns={normalized_alias: standard_name}
                    )
                    break

    # Handle datasets containing Sales and Profit
    if "sales" in df.columns and "quantity" in df.columns:
        df["unit_price"] = (
            df["sales"] / df["quantity"].replace(0, 1)
        )

    if "profit" in df.columns and "sales" in df.columns and "quantity" in df.columns:
        df["unit_cost"] = (
            (df["sales"] - df["profit"]) /
            df["quantity"].replace(0, 1)
        )



    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Add optional columns if they are absent
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = "Unknown"

    # Remove exact duplicate records
    duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Convert dates
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "quantity", "unit_price", "unit_cost"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove records with missing essential information
    rows_before_missing = len(df)

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    ).copy()

    missing_rows_removed = rows_before_missing - len(df)

    # Remove invalid values
    rows_before_validation = len(df)

    df = df[
        (df["quantity"] > 0) &
        (df["unit_price"] >= 0) &
        (df["unit_cost"] >= 0)
    ].copy()

    invalid_rows_removed = (
        rows_before_validation - len(df)
    )

    # Clean optional text fields
    for col in OPTIONAL_COLUMNS:
        df[col] = (
            df[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

    # Calculate business metrics
    df["revenue"] = (
        df["quantity"] * df["unit_price"]
    )

    df["total_cost"] = (
        df["quantity"] * df["unit_cost"]
    )

    df["profit"] = (
        df["revenue"] - df["total_cost"]
    )

    df["profit_margin_pct"] = (
        df["profit"] /
        df["revenue"].where(df["revenue"] != 0, 1)
        * 100
    ).round(2)

    # Generate monthly analysis column
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    # Sort by order date
    df = df.sort_values("order_date").reset_index(drop=True)

    # Data quality report
    quality_report = {
        "original_rows": original_rows,
        "final_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "missing_rows_removed": missing_rows_removed,
        "invalid_rows_removed": invalid_rows_removed,
        "total_rows_removed": original_rows - len(df)
    }

    return df, quality_report


# --------------------------------------------------
# 4. CALCULATE BUSINESS KPIs
# --------------------------------------------------

def calculate_kpis(df):

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_units = df["quantity"].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0 else 0
    )

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue > 0 else 0
    )

    kpis = {
        "Total Revenue": total_revenue,
        "Total Profit": total_profit,
        "Total Orders": total_orders,
        "Units Sold": total_units,
        "Average Order Value": average_order_value,
        "Profit Margin": profit_margin
    }

    return kpis

# --------------------------------------------------
# 5. GENERATE BUSINESS ANALYTICS
# --------------------------------------------------

def generate_analytics(df):

    # Monthly sales analysis
    monthly = (
        df.groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("month")
    )

    # Region-wise analysis
    region = (
        df.groupby("region")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    # Product-wise analysis
    product = (
        df.groupby("product")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            units_sold=("quantity", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    # Category-wise analysis
    category = (
        df.groupby("category")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    # Sales representative analysis
    sales_rep = (
        df.groupby("sales_rep")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    return {
        "monthly": monthly,
        "region": region,
        "product": product,
        "category": category,
        "sales_rep": sales_rep
    }


# --------------------------------------------------
# 6. CALCULATE BUSINESS KPIs
# --------------------------------------------------

def calculate_kpis(df):

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_units = df["quantity"].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0 else 0
    )

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue > 0 else 0
    )

    kpis = {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_units": total_units,
        "average_order_value": average_order_value,
        "profit_margin": profit_margin
    }

    return kpis



# --------------------------------------------------
# 7. DISPLAY BUSINESS DASHBOARD
# --------------------------------------------------

def show_dashboard(df, kpis, analytics):

    st.subheader("Business Performance Overview")

    # KPI CARDS
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Revenue",
        f"₹{kpis.get('total_revenue', kpis.get('revenue', 0)):,.2f}"
    )

    col2.metric(
        "Total Profit",
        f"₹{kpis.get('total_profit', kpis.get('profit', 0)):,.2f}"
    )

    col3.metric(
        "Total Orders",
        f"{kpis.get('total_orders', kpis.get('orders', 0)):,}"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Units Sold",
        f"{kpis.get('total_units', kpis.get('units_sold', 0)):,}"
    )

    col5.metric(
        "Average Order Value",
        f"₹{kpis.get('average_order_value', 0):,.2f}"
    )

    col6.metric(
        "Profit Margin",
        f"{kpis.get('profit_margin', 0):.2f}%"
    )

    st.divider()

    # MONTHLY REVENUE CHART
    st.subheader("Monthly Revenue Trend")

    monthly = analytics["monthly"]

    if not monthly.empty:
        st.line_chart(
            monthly.set_index("month")[["revenue"]]
        )

    # REGION-WISE ANALYSIS
    st.subheader("Region-wise Sales Performance")

    region = analytics["region"]

    if not region.empty:
        st.bar_chart(
            region.set_index("region")[["revenue"]]
        )

    # PRODUCT-WISE ANALYSIS
    st.subheader("Top Performing Products")

    product = analytics["product"]

    if not product.empty:
        st.bar_chart(
            product.set_index("product")[["revenue"]]
        )

    # CATEGORY ANALYSIS
    st.subheader("Category-wise Performance")

    category = analytics["category"]

    if not category.empty:
        st.dataframe(category, use_container_width=True)

    # SALES REPRESENTATIVE ANALYSIS
    st.subheader("Sales Representative Performance")

    sales_rep = analytics["sales_rep"]

    if not sales_rep.empty:
        st.dataframe(sales_rep, use_container_width=True)

    # CLEANED DATA
    st.subheader("Processed Sales Data")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


# --------------------------------------------------
# 8. GENERATE EXCEL BUSINESS REPORT
# --------------------------------------------------

def create_excel_report(df, kpis, analytics, quality):

    from io import BytesIO
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.chart import BarChart, LineChart, Reference
    from openpyxl.utils import get_column_letter

    output = BytesIO()

    # Prepare KPI summary
    kpi_summary = pd.DataFrame({
        "KPI": list(kpis.keys()),
        "Value": list(kpis.values())
    })

    # Prepare data quality report
    quality_df = pd.DataFrame({
        "Metric": list(quality.keys()),
        "Value": list(quality.values())
    })

    # Create Excel workbook with multiple sheets
    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        kpi_summary.to_excel(
            writer, sheet_name="KPI Summary", index=False
        )

        df.to_excel(
            writer, sheet_name="Cleaned Data", index=False
        )

        analytics["monthly"].to_excel(
            writer, sheet_name="Monthly Sales", index=False
        )

        analytics["region"].to_excel(
            writer, sheet_name="Region Analysis", index=False
        )

        analytics["product"].to_excel(
            writer, sheet_name="Product Analysis", index=False
        )

        analytics["category"].to_excel(
            writer, sheet_name="Category Analysis", index=False
        )

        analytics["sales_rep"].to_excel(
            writer, sheet_name="Sales Rep Analysis", index=False
        )

        quality_df.to_excel(
            writer, sheet_name="Data Quality", index=False
        )
        

        workbook = writer.book
        # ------------------------------------------------
        # ADD CHARTS TO EXCEL REPORT
        # ------------------------------------------------

        charts_sheet = workbook.create_sheet("Charts")

        # 1. Monthly Revenue Trend - Line Chart
        monthly_sheet = workbook["Monthly Sales"]

        monthly_chart = LineChart()
        monthly_chart.title = "Monthly Revenue Trend"
        monthly_chart.style = 13
        monthly_chart.y_axis.title = "Revenue (INR)"
        monthly_chart.x_axis.title = "Month"
        monthly_chart.height = 9
        monthly_chart.width = 18

        monthly_data = Reference(
            monthly_sheet,
            min_col=2,
            min_row=1,
            max_row=monthly_sheet.max_row
        )

        monthly_categories = Reference(
            monthly_sheet,
            min_col=1,
            min_row=2,
            max_row=monthly_sheet.max_row
        )

        monthly_chart.add_data(
            monthly_data,
            titles_from_data=True
        )

        monthly_chart.set_categories(monthly_categories)

        charts_sheet.add_chart(monthly_chart, "A1")

        # 2. Region-wise Revenue - Column Chart
        region_sheet = workbook["Region Analysis"]

        region_chart = BarChart()
        region_chart.type = "col"
        region_chart.style = 10
        region_chart.title = "Region-wise Revenue"
        region_chart.y_axis.title = "Revenue (INR)"
        region_chart.x_axis.title = "Region"
        region_chart.height = 9
        region_chart.width = 18

        region_data = Reference(
            region_sheet,
            min_col=2,
            min_row=1,
            max_row=region_sheet.max_row
        )

        region_categories = Reference(
            region_sheet,
            min_col=1,
            min_row=2,
            max_row=region_sheet.max_row
        )

        region_chart.add_data(
            region_data,
            titles_from_data=True
        )

        region_chart.set_categories(region_categories)

        charts_sheet.add_chart(region_chart, "J1")

        # 3. Product-wise Revenue - Bar Chart
        product_sheet = workbook["Product Analysis"]

        product_chart = BarChart()
        product_chart.type = "bar"
        product_chart.style = 11
        product_chart.title = "Product-wise Revenue"
        product_chart.x_axis.title = "Revenue (INR)"
        product_chart.y_axis.title = "Product"
        product_chart.height = 12
        product_chart.width = 22

        product_data = Reference(
            product_sheet,
            min_col=2,
            min_row=1,
            max_row=product_sheet.max_row
        )

        product_categories = Reference(
            product_sheet,
            min_col=1,
            min_row=2,
            max_row=product_sheet.max_row
        )

        product_chart.add_data(
            product_data,
            titles_from_data=True
        )

        product_chart.set_categories(product_categories)

        charts_sheet.add_chart(product_chart, "A20")

        
        # ------------------------------------------------
        # FORMAT ALL WORKSHEETS
        # ------------------------------------------------

        currency_headers = {
            "revenue",
            "profit",
            "total_cost",
            "unit_price",
            "unit_cost",
            "average_order_value"
        }

        percentage_headers = {
            "profit_margin_pct",
            "profit_margin"
        }

        for worksheet in workbook.worksheets:

            # Format header row
            for cell in worksheet[1]:
                cell.font = Font(
                    bold=True,
                    color="FFFFFF"
                )

                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor="1F4E78"
                )

                cell.alignment = Alignment(
                    horizontal="center"
                )

            # Freeze header row
            worksheet.freeze_panes = "A2"

            # Enable filters (except Charts sheet)
            if worksheet.title != "Charts":
                worksheet.auto_filter.ref = worksheet.dimensions

            # Adjust column widths
            for column_cells in worksheet.columns:

                max_length = 0

                column_letter = get_column_letter(
                    column_cells[0].column
                )

                for cell in column_cells:
                    if cell.value is not None:
                        max_length = max(
                            max_length,
                            len(str(cell.value))
                        )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(max(max_length + 5, 18), 40)

            # Apply currency and percentage formatting
            if worksheet.title != "Charts":

                for column_cells in worksheet.columns:

                    header = str(
                        column_cells[0].value
                    ).strip().lower()

                    # Currency formatting
                    if header in currency_headers:

                        for cell in column_cells[1:]:
                            if isinstance(cell.value, (int, float)):
                                cell.number_format = '"₹" #,##0.00'
                                cell.font = Font(name="Arial", size=10)

                    # Percentage formatting
                    elif header in percentage_headers:

                        for cell in column_cells[1:]:
                            if isinstance(cell.value, (int, float)):
                                cell.number_format = '0.00"%"'

            # Special formatting for KPI Summary
            if worksheet.title == "KPI Summary":

                for row in worksheet.iter_rows(min_row=2):

                    kpi_name = str(
                        row[0].value
                    ).strip().lower()

                    value_cell = row[1]

                    if kpi_name in {
                        "total_revenue",
                        "total_profit",
                        "average_order_value"
                    }:
                        value_cell.number_format = '"₹" #,##0.00'
                        value_cell.font = Font(
                            name="Arial",
                            size=11
                        )

                    elif kpi_name == "profit_margin":
                        value_cell.number_format = '0.00"%"'

    output.seek(0)

    return output





# --------------------------------------------------
# MAIN STREAMLIT APPLICATION
# --------------------------------------------------



def apply_dashboard_filters(df):

    st.subheader("Dashboard Filters")

    # Create three columns for dropdown filters
    col1, col2, col3 = st.columns(3)

    # 1. Date Filter
    with col1:
        min_date = df["order_date"].min().date()
        max_date = df["order_date"].max().date()

        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    # 2. Region Filter
    with col2:
        regions = ["All"] + sorted(df["region"].dropna().unique().tolist())

        selected_region = st.selectbox(
            "Select Region",
            options=regions
        )

    # 3. Product Filter
    with col3:
        products = ["All"] + sorted(df["product"].dropna().unique().tolist())

        selected_product = st.selectbox(
            "Select Product",
            options=products
        )

    # Category dropdown
    categories = ["All"] + sorted(
        df["category"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Select Category",
        options=categories
    )

    # Handle date selection
    if isinstance(date_range, (tuple, list)):
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_range

    # Apply filters
    filtered_df = df[
        (df["order_date"].dt.date >= start_date) &
        (df["order_date"].dt.date <= end_date)
    ].copy()

    if selected_region != "All":
        filtered_df = filtered_df[
            filtered_df["region"] == selected_region
        ]

    if selected_product != "All":
        filtered_df = filtered_df[
            filtered_df["product"] == selected_product
        ]

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    return filtered_df


def main():

    st.set_page_config(
        page_title="Automated Business Reporting",
        page_icon="📊",
        layout="wide"
    )

    st.title("Automated Business Reporting System")
    st.caption("Business analytics and automated reporting dashboard")

    uploaded_files = st.file_uploader(
        "Upload CSV or Excel sales files",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:

        try:
            # Load uploaded datasets
            dataframes = [
                load_file(file) for file in uploaded_files
            ]

            raw_data = pd.concat(
                dataframes,
                ignore_index=True
            )

            
            # Clean data
            cleaned_data, quality = clean_data(raw_data)

            # Apply interactive dashboard filters
            filtered_data = apply_dashboard_filters(cleaned_data)

            # Check whether filtered data is empty
            if filtered_data.empty:
                st.warning("No records found for the selected filters.")
                st.stop()

            # Calculate business KPIs using filtered data
            kpis = calculate_kpis(filtered_data)

            # Generate analytics using filtered data
            analytics = generate_analytics(filtered_data)

            # Display dashboard using filtered data
            show_dashboard(
                filtered_data,
                kpis,
                analytics
            )


            # Display data quality
            st.subheader("Data Quality Report")
            st.json(quality)

            # Download Excel report
            excel_file = create_excel_report(
                cleaned_data,
                kpis,
                analytics,
                quality
            )

            st.download_button(
                label="Download Excel Report",
                data=excel_file,
                file_name="Business_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as error:
            st.error(f"An error occurred: {error}")

    else:
        st.info("Upload one or more CSV or Excel files to generate your dashboard.")


# Run application
if __name__ == "__main__":
    main()


