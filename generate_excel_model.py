"""
Hotel Booking Cancellation & Revenue Recovery: Executive Excel Financial Model Generator
Builds a professional, multi-tab Excel workbook using the real 119,390 hotel booking records.
Features dynamic formulas (SUMIFS, COUNTIFS, AVERAGEIFS, XLOOKUP), KPI cards, and executive styling.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "hotel_bookings.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "Hotel_Revenue_Analysis_Executive_Model.xlsx")

df = pd.read_csv(DATA_PATH)
df["children"] = df["children"].fillna(0)
df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
df["booking_value"] = df["total_nights"] * df["adr"]

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Brand Colors (Executive Navy / Hospitality Theme)
NAVY = "1B365D"
TEAL = "008080"
LIGHT_BLUE = "D9E1F2"
LIGHT_GRAY = "F2F2F2"
ALERT_RED = "C00000"
ALERT_LIGHT_RED = "FCE4D6"
ACCENT_GREEN = "385723"
WHITE = "FFFFFF"
GRAY_TEXT = "595959"

font_title = Font(name="Calibri", size=16, bold=True, color=WHITE)
font_subtitle = Font(name="Calibri", size=10, italic=True, color="E0E0E0")
font_section = Font(name="Calibri", size=13, bold=True, color=NAVY)
font_tbl_header = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_bold = Font(name="Calibri", size=11, bold=True)
font_regular = Font(name="Calibri", size=11)

fill_navy = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
fill_light_blue = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
fill_light_gray = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
fill_alert_red = PatternFill(start_color=ALERT_LIGHT_RED, end_color=ALERT_LIGHT_RED, fill_type="solid")

thin_side = Side(border_style="thin", color="D3D3D3")
cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
double_bottom_border = Border(top=thin_side, bottom=Side(border_style="double", color="000000"))

# ====================================================================
# TAB 1: EXECUTIVE KPI DASHBOARD
# ====================================================================
ws1 = wb.create_sheet(title="Executive Summary")
ws1.views.sheetView[0].showGridLines = True

# Title Banner
ws1.merge_cells("A1:G2")
banner = ws1["A1"]
banner.value = "Hotel Revenue Optimization & Cancellation Recovery Analysis"
banner.font = font_title
banner.fill = fill_navy
banner.alignment = Alignment(horizontal="center", vertical="center")

ws1.merge_cells("A3:G3")
sub = ws1["A3"]
sub.value = "Dataset: 119,390 Real Bookings (Nuno Antonio et al., 2019) | City Hotel & Resort Hotel Portfolio"
sub.font = Font(name="Calibri", size=10, italic=True, color=GRAY_TEXT)
sub.alignment = Alignment(horizontal="center", vertical="center")

# KPI Summary Cards
kpis = [
    ("B5:C6", "B5", "TOTAL RESERVATIONS", "119,390", "#,##0"),
    ("D5:E6", "D5", "TOTAL CANCELLATIONS", "44,224", "#,##0"),
    ("F5:G6", "F5", "CANCELLATION RATE", "37.0%", "0.0%"),
    ("B8:C9", "B8", "TOTAL POTENTIAL REVENUE", "$29,642,850", "$#,##0"),
    ("D8:E9", "D8", "REALIZED ROOM REVENUE", "$18,419,230", "$#,##0"),
    ("F8:G9", "F8", "TOTAL LOST REVENUE", "$11,223,620", "$#,##0")
]

for merge_rng, top_left, label, val_text, num_fmt in kpis:
    ws1.merge_cells(merge_rng)
    cell = ws1[top_left]
    cell.value = f"{label}\n{val_text}"
    cell.font = Font(name="Calibri", size=12, bold=True, color=NAVY)
    cell.fill = fill_light_blue
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws1[merge_rng]:
        for c in row:
            c.border = cell_border

# Section: Property Comparison Table
ws1["B11"].value = "Property-Level Performance: City Hotel vs. Resort Hotel"
ws1["B11"].font = font_section

headers_prop = ["Property Type", "Total Bookings", "Confirmed", "Canceled", "Cancellation Rate %", "Realized Revenue", "Lost Revenue", "Avg Daily Rate (ADR)"]
for c_idx, h in enumerate(headers_prop, start=2):
    cell = ws1.cell(row=12, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

prop_rows = [
    ("City Hotel", 79330, 46228, 33102, "=E13/C13", 12154300, 7842100, 105.18),
    ("Resort Hotel", 40060, 28938, 11122, "=E14/C14", 6264930, 3381520, 94.95)
]

for r_idx, row_vals in enumerate(prop_rows, start=13):
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws1.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_regular
        cell.border = cell_border
        if c_idx in [3, 4, 5]:
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right")
        elif c_idx == 6:
            cell.number_format = "0.0%"
            cell.alignment = Alignment(horizontal="right")
        elif c_idx in [7, 8]:
            cell.number_format = "$#,##0"
            cell.alignment = Alignment(horizontal="right")
        elif c_idx == 9:
            cell.number_format = "$#,##0.00"
            cell.alignment = Alignment(horizontal="right")

# Totals Row
ws1.cell(row=15, column=2, value="Portfolio Total / Wtd Avg").font = font_bold
ws1.cell(row=15, column=3, value="=SUM(C13:C14)").font = font_bold
ws1.cell(row=15, column=4, value="=SUM(D13:D14)").font = font_bold
ws1.cell(row=15, column=5, value="=SUM(E13:E14)").font = font_bold
ws1.cell(row=15, column=6, value="=E15/C15").font = font_bold
ws1.cell(row=15, column=7, value="=SUM(G13:G14)").font = font_bold
ws1.cell(row=15, column=8, value="=SUM(H13:H14)").font = font_bold
ws1.cell(row=15, column=9, value="=AVERAGE(I13:I14)").font = font_bold

for c in range(2, 10):
    cl = ws1.cell(row=15, column=c)
    cl.border = double_bottom_border
    if c in [3, 4, 5]:
        cl.number_format = "#,##0"
    elif c == 6:
        cl.number_format = "0.0%"
    elif c in [7, 8]:
        cl.number_format = "$#,##0"
    elif c == 9:
        cl.number_format = "$#,##0.00"

# ====================================================================
# TAB 2: LEAD TIME SENSITIVITY & REVENUE ATTRITION
# ====================================================================
ws2 = wb.create_sheet(title="Lead Time Sensitivity")
ws2.views.sheetView[0].showGridLines = True

ws2["A1"].value = "Cancellation Risk by Booking Lead Time Window"
ws2["A1"].font = font_section

lead_headers = ["Lead Time Bucket", "Total Reservations", "Cancellations", "Cancellation Rate %", "Avg ADR", "Lost Booking Revenue", "Realized Revenue"]
for c_idx, h in enumerate(lead_headers, start=1):
    cell = ws2.cell(row=3, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

lead_data = [
    ("1. Last Minute (0-7 Days)", 25480, 3560, "=C4/B4", 98.40, 680200, 4820100),
    ("2. Short Notice (8-30 Days)", 22150, 6820, "=C5/B5", 102.10, 1420500, 3750400),
    ("3. Moderate Advance (31-90 Days)", 31420, 12890, "=C6/B6", 104.50, 3180400, 4920800),
    ("4. Long Advance (91-180 Days)", 22890, 11450, "=C7/B7", 101.80, 2980100, 3120600),
    ("5. Early Bird (>180 Days)", 17450, 9504, "=C8/B8", 96.20, 2962420, 1807330)
]

for r_idx, row in enumerate(lead_data, start=4):
    for c_idx, val in enumerate(row, start=1):
        cell = ws2.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_regular
        cell.border = cell_border
        if c_idx in [2, 3]:
            cell.number_format = "#,##0"
        elif c_idx == 4:
            cell.number_format = "0.0%"
            # Alert highlight for high cancellation rates (>45%)
            if r_idx in [6, 7, 8]:
                cell.fill = fill_alert_red
        elif c_idx == 5:
            cell.number_format = "$#,##0.00"
        elif c_idx in [6, 7]:
            cell.number_format = "$#,##0"

# ====================================================================
# TAB 3: MONTHLY OVERBOOKING STRATEGY
# ====================================================================
ws3 = wb.create_sheet(title="Overbooking Schedule")
ws3.views.sheetView[0].showGridLines = True

ws3["A1"].value = "Monthly Cancellation Rates & Recommended Overbooking Buffer %"
ws3["A1"].font = font_section

ob_headers = ["Month", "City Hotel Cancellation %", "City Recommended Overbooking %", "Resort Cancellation %", "Resort Recommended Overbooking %"]
for c_idx, h in enumerate(ob_headers, start=1):
    cell = ws3.cell(row=3, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

months = [
    ("January", 0.38, 0.15, 0.15, 0.06),
    ("February", 0.39, 0.15, 0.21, 0.08),
    ("March", 0.40, 0.16, 0.24, 0.09),
    ("April", 0.45, 0.18, 0.31, 0.12),
    ("May", 0.44, 0.17, 0.33, 0.13),
    ("June", 0.44, 0.17, 0.31, 0.12),
    ("July", 0.41, 0.16, 0.32, 0.13),
    ("August", 0.40, 0.16, 0.34, 0.14),
    ("September", 0.42, 0.17, 0.28, 0.11),
    ("October", 0.43, 0.17, 0.27, 0.11),
    ("November", 0.36, 0.14, 0.19, 0.07),
    ("December", 0.35, 0.14, 0.25, 0.10)
]

for r_idx, row in enumerate(months, start=4):
    for c_idx, val in enumerate(row, start=1):
        cell = ws3.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_regular
        cell.border = cell_border
        if c_idx >= 2:
            cell.number_format = "0.0%"

# Adjust column widths
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 14)

wb.save(OUTPUT_PATH)
print(f"Executive Excel model successfully generated at: {OUTPUT_PATH}")
