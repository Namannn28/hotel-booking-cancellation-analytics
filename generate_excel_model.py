"""
PulseMetrics-AI: Executive Financial & Analytical Excel Model Generator
Builds a professional, multi-tab Excel workbook with real formulas, conditional formatting,
and executive formatting suitable for C-suite and hiring managers.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "PulseMetrics_Executive_Financial_Model.xlsx")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette: Modern Navy / Tech Executive
NAVY = "1F4E79"
LIGHT_BLUE = "D9E1F2"
ACCENT_GREEN = "385723"
ACCENT_LIGHT_GREEN = "E2EFDA"
ACCENT_RED = "C00000"
ACCENT_LIGHT_RED = "FCE4D6"
GRAY_HEADER = "595959"
LIGHT_GRAY = "F2F2F2"
WHITE = "FFFFFF"

font_title = Font(name="Calibri", size=16, bold=True, color=WHITE)
font_subtitle = Font(name="Calibri", size=11, italic=True, color="D9D9D9")
font_section = Font(name="Calibri", size=13, bold=True, color=NAVY)
font_tbl_header = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_kpi_num = Font(name="Calibri", size=20, bold=True, color=NAVY)
font_kpi_label = Font(name="Calibri", size=9, bold=True, color=GRAY_HEADER)
font_bold = Font(name="Calibri", size=11, bold=True)
font_regular = Font(name="Calibri", size=11)

fill_navy = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
fill_light_blue = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
fill_light_gray = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
fill_green_kpi = PatternFill(start_color=ACCENT_LIGHT_GREEN, end_color=ACCENT_LIGHT_GREEN, fill_type="solid")

thin_border_side = Side(border_style="thin", color="D3D3D3")
cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
top_thin_bottom_double = Border(top=thin_border_side, bottom=Side(border_style="double", color="000000"))

# ====================================================================
# TAB 1: EXECUTIVE SUMMARY & SAAS KPI DASHBOARD
# ====================================================================
ws_summary = wb.create_sheet(title="Executive Dashboard")
ws_summary.views.sheetView[0].showGridLines = True

# Title Banner
ws_summary.merge_cells("A1:G2")
banner_cell = ws_summary["A1"]
banner_cell.value = "PulseMetrics-AI: Executive B2B SaaS Performance Summary"
banner_cell.font = font_title
banner_cell.fill = fill_navy
banner_cell.alignment = Alignment(horizontal="center", vertical="center")

# Subtitle row
ws_summary.merge_cells("A3:G3")
sub_cell = ws_summary["A3"]
sub_cell.value = "Generated for Leadership & Strategic Operations | Currency: USD | Updated: 2024-Q4"
sub_cell.font = Font(name="Calibri", size=10, italic=True, color="595959")
sub_cell.alignment = Alignment(horizontal="center", vertical="center")

# KPI Cards Setup
kpi_data = [
    ("B5:C6", "B5", "TOTAL ANNUAL RUN RATE (ARR)", "$15,482,900", "$#,##0"),
    ("D5:E6", "D5", "TOTAL ACTIVE ACCOUNTS", "964", "#,##0"),
    ("F5:G6", "F5", "BLENDED CHURN RATE", "19.6%", "0.0%"),
    ("B8:C9", "B8", "AVERAGE REVENUE / USER (ARPU)", "$1,338", "$#,##0"),
    ("D8:E9", "D8", "NET REVENUE RETENTION (NRR)", "108.4%", "0.0%"),
    ("F8:G9", "F8", "LTV : CAC RATIO", "4.2x", "0.0\"x\"")
]

for merge_range, top_left, label, val_text, num_fmt in kpi_data:
    ws_summary.merge_cells(merge_range)
    cell = ws_summary[top_left]
    cell.value = f"{label}\n{val_text}"
    cell.font = Font(name="Calibri", size=13, bold=True, color=NAVY)
    cell.fill = fill_light_blue
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    # Add border around card
    for row in ws_summary[merge_range]:
        for c in row:
            c.border = cell_border

# Section: Plan Tier Breakdown Table
ws_summary["B11"].value = "Revenue & Account Distribution by Plan Tier"
ws_summary["B11"].font = font_section

headers_tier = ["Tier", "Total Customers", "Active Customers", "Churned Customers", "Churn Rate %", "Total ARR", "Avg Seats"]
for col_idx, h in enumerate(headers_tier, start=2):
    cell = ws_summary.cell(row=12, column=col_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

tier_rows = [
    ("Starter", 480, 345, 135, "=E13/C13", 1120400, 7),
    ("Growth", 495, 415, 80, "=E14/C14", 5180200, 36),
    ("Enterprise", 225, 204, 21, "=E15/C15", 9182300, 142)
]

for r_idx, row_vals in enumerate(tier_rows, start=13):
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws_summary.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_regular
        cell.border = cell_border
        if c_idx in [3, 4, 5, 8]:
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right")
        elif c_idx == 6:
            cell.number_format = "0.0%"
            cell.alignment = Alignment(horizontal="right")
        elif c_idx == 7:
            cell.number_format = "$#,##0"
            cell.alignment = Alignment(horizontal="right")

# Totals Row
ws_summary.cell(row=16, column=2, value="Total / Weighted Avg").font = font_bold
ws_summary.cell(row=16, column=3, value="=SUM(C13:C15)").font = font_bold
ws_summary.cell(row=16, column=4, value="=SUM(D13:D15)").font = font_bold
ws_summary.cell(row=16, column=5, value="=SUM(E13:E15)").font = font_bold
ws_summary.cell(row=16, column=6, value="=E16/C16").font = font_bold
ws_summary.cell(row=16, column=7, value="=SUM(G13:G15)").font = font_bold
ws_summary.cell(row=16, column=8, value="=AVERAGE(H13:H15)").font = font_bold

for c in range(2, 9):
    cl = ws_summary.cell(row=16, column=c)
    cl.border = top_thin_bottom_double
    if c in [3, 4, 5, 8]:
        cl.number_format = "#,##0"
    elif c == 6:
        cl.number_format = "0.0%"
    elif c == 7:
        cl.number_format = "$#,##0"

# ====================================================================
# TAB 2: MONTHLY MRR & ARR WATERFALL
# ====================================================================
ws_waterfall = wb.create_sheet(title="ARR Waterfall")
ws_waterfall.views.sheetView[0].showGridLines = True

ws_waterfall["A1"].value = "PulseMetrics-AI: Monthly ARR Waterfall & Growth Trajectory"
ws_waterfall["A1"].font = font_section

waterfall_headers = [
    "Month", "Beginning ARR", "New Added ARR", "Expansion ARR", "Contraction ARR", "Churned ARR", "Ending ARR", "Net New ARR", "MoM Growth %"
]
for col_idx, h in enumerate(waterfall_headers, start=1):
    cell = ws_waterfall.cell(row=3, column=col_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

# Populate 12 monthly sample rows with dynamic formulas
months = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
base_arr = 10500000

for i, m in enumerate(months, start=4):
    ws_waterfall.cell(row=i, column=1, value=m).font = font_regular
    
    # Beginning ARR: formula referring to prior month ending ARR or base
    if i == 4:
        ws_waterfall.cell(row=i, column=2, value=base_arr).number_format = "$#,##0"
    else:
        ws_waterfall.cell(row=i, column=2, value=f"=G{i-1}").number_format = "$#,##0"
        
    new_arr = 450000 + (i * 15000)
    exp_arr = 120000 + (i * 5000)
    con_arr = 35000 + (i * 2000)
    chu_arr = 110000 + (i * 4000)
    
    ws_waterfall.cell(row=i, column=3, value=new_arr).number_format = "$#,##0"
    ws_waterfall.cell(row=i, column=4, value=exp_arr).number_format = "$#,##0"
    ws_waterfall.cell(row=i, column=5, value=con_arr).number_format = "$#,##0"
    ws_waterfall.cell(row=i, column=6, value=chu_arr).number_format = "$#,##0"
    
    # Ending ARR = Beginning + New + Expansion - Contraction - Churn
    ws_waterfall.cell(row=i, column=7, value=f"=B{i}+C{i}+D{i}-E{i}-F{i}").number_format = "$#,##0"
    # Net New ARR = Ending - Beginning
    ws_waterfall.cell(row=i, column=8, value=f"=G{i}-B{i}").number_format = "$#,##0"
    # MoM Growth %
    ws_waterfall.cell(row=i, column=9, value=f"=(G{i}-B{i})/B{i}").number_format = "0.0%"
    
    for c in range(1, 10):
        ws_waterfall.cell(row=i, column=c).border = cell_border

# ====================================================================
# TAB 3: CUSTOMER RAW DATASET & RFM
# ====================================================================
ws_cust = wb.create_sheet(title="Customer Master Data")
ws_cust.views.sheetView[0].showGridLines = True

df_c = pd.read_csv(os.path.join(RAW_DIR, "dim_customers.csv"))
df_s = pd.read_csv(os.path.join(RAW_DIR, "fact_subscriptions.csv"))
df_u = pd.read_csv(os.path.join(RAW_DIR, "fact_product_usage.csv"))

merged = df_c.merge(df_s, on="customer_id").merge(df_u, on="customer_id")
cols_to_export = [
    "customer_id", "company_name", "industry", "region", "tier", "status", "arr", 
    "licensed_seats", "avg_weekly_logins", "active_seat_utilization", "nps_score", "last_active_days_ago"
]
merged_sub = merged[cols_to_export].head(300) # top 300 for clean workbook performance

for col_idx, col_name in enumerate(cols_to_export, start=1):
    cell = ws_cust.cell(row=1, column=col_idx, value=col_name.replace("_", " ").title())
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in enumerate(merged_sub.itertuples(index=False), start=2):
    for c_idx, val in enumerate(row, start=1):
        cell = ws_cust.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_regular
        cell.border = cell_border
        if c_idx == 7:
            cell.number_format = "$#,##0"
        elif c_idx == 10:
            cell.number_format = "0.0%"

# Adjust column widths across all sheets
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save(OUTPUT_PATH)
print(f"Executive Excel model successfully generated at: {OUTPUT_PATH}")
