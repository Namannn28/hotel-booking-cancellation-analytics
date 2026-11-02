"""
Hotel Revenue & Cancellation Financial Model Generator
Author: Naman Gupta

Creates an executive Excel workbook summarizing property performance,
revenue loss from cancellations, lead-time sensitivity, and dynamic overbooking buffers.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(__file__)
OUTPUT_WORKBOOK_PATH = os.path.join(BASE_DIR, "data", "Hotel_Revenue_Analysis_Executive_Model.xlsx")


def create_executive_excel_model():
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)  # Remove default blank sheet

    # Executive Color Palette (Hospitality Navy & Clean Grayscale)
    NAVY_BLUE = "1B365D"
    SOFT_BLUE = "D9E1F2"
    LIGHT_GRAY = "F8F9FA"
    ALERT_RED = "FCE4D6"
    WHITE = "FFFFFF"
    DARK_GRAY = "333333"

    font_banner = Font(name="Calibri", size=15, bold=True, color=WHITE)
    font_section = Font(name="Calibri", size=12, bold=True, color=NAVY_BLUE)
    font_header = Font(name="Calibri", size=10, bold=True, color=WHITE)
    font_bold = Font(name="Calibri", size=10, bold=True, color=DARK_GRAY)
    font_cell = Font(name="Calibri", size=10, color=DARK_GRAY)

    fill_navy = PatternFill(start_color=NAVY_BLUE, end_color=NAVY_BLUE, fill_type="solid")
    fill_soft_blue = PatternFill(start_color=SOFT_BLUE, end_color=SOFT_BLUE, fill_type="solid")
    fill_alert = PatternFill(start_color=ALERT_RED, end_color=ALERT_RED, fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0")
    )
    total_border = Border(
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000")
    )

    # -------------------------------------------------------------------------
    # Sheet 1: Executive KPI Summary
    # -------------------------------------------------------------------------
    sheet_kpi = workbook.create_sheet(title="Executive Summary")
    sheet_kpi.views.sheetView[0].showGridLines = True

    # Title Banner
    sheet_kpi.merge_cells("A1:G2")
    banner_cell = sheet_kpi["A1"]
    banner_cell.value = "Hotel Revenue Optimization & Cancellation Recovery Analysis"
    banner_cell.font = font_banner
    banner_cell.fill = fill_navy
    banner_cell.alignment = Alignment(horizontal="center", vertical="center")

    sheet_kpi.merge_cells("A3:G3")
    subtitle_cell = sheet_kpi["A3"]
    subtitle_cell.value = "Operational Analysis across 119,390 Real Bookings | City Hotel & Resort Hotel Portfolio"
    subtitle_cell.font = Font(name="Calibri", size=9, italic=True, color="666666")
    subtitle_cell.alignment = Alignment(horizontal="center", vertical="center")

    # High-Level KPI Summary Cards
    kpi_metric_cards = [
        ("B5:C6", "B5", "TOTAL RESERVATIONS\n119,390"),
        ("D5:E6", "D5", "TOTAL CANCELLATIONS\n44,224"),
        ("F5:G6", "F5", "CANCELLATION RATE\n37.0%"),
        ("B8:C9", "B8", "POTENTIAL REVENUE\n$29,642,850"),
        ("D8:E9", "D8", "REALIZED REVENUE\n$18,419,230"),
        ("F8:G9", "F8", "LOST REVENUE\n$11,223,620")
    ]

    for cell_range, top_left_cell, text_value in kpi_metric_cards:
        sheet_kpi.merge_cells(cell_range)
        target_cell = sheet_kpi[top_left_cell]
        target_cell.value = text_value
        target_cell.font = font_section
        target_cell.fill = fill_soft_blue
        target_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in sheet_kpi[cell_range]:
            for single_cell in row:
                single_cell.border = thin_border

    # Property-Level Performance Breakdown
    sheet_kpi["B11"].value = "Property-Level Breakdown"
    sheet_kpi["B11"].font = font_section

    table_headers = [
        "Property", "Total Bookings", "Confirmed", "Canceled",
        "Cancellation Rate %", "Realized Revenue", "Lost Revenue", "Average Daily Rate"
    ]
    for column_index, header_text in enumerate(table_headers, start=2):
        header_cell = sheet_kpi.cell(row=12, column=column_index, value=header_text)
        header_cell.font = font_header
        header_cell.fill = fill_navy
        header_cell.alignment = Alignment(horizontal="center", vertical="center")

    property_data = [
        ("City Hotel", 79330, 46228, 33102, "=E13/C13", 12154300, 7842100, 105.18),
        ("Resort Hotel", 40060, 28938, 11122, "=E14/C14", 6264930, 3381520, 94.95)
    ]

    for row_index, property_values in enumerate(property_data, start=13):
        for col_index, value in enumerate(property_values, start=2):
            cell = sheet_kpi.cell(row=row_index, column=col_index, value=value)
            cell.font = font_cell
            cell.border = thin_border
            if col_index in [3, 4, 5]:
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right")
            elif col_index == 6:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            elif col_index in [7, 8]:
                cell.number_format = "$#,##0"
                cell.alignment = Alignment(horizontal="right")
            elif col_index == 9:
                cell.number_format = "$#,##0.00"
                cell.alignment = Alignment(horizontal="right")

    # Summary Totals Row
    sheet_kpi.cell(row=15, column=2, value="Portfolio Total").font = font_bold
    sheet_kpi.cell(row=15, column=3, value="=SUM(C13:C14)").font = font_bold
    sheet_kpi.cell(row=15, column=4, value="=SUM(D13:D14)").font = font_bold
    sheet_kpi.cell(row=15, column=5, value="=SUM(E13:E14)").font = font_bold
    sheet_kpi.cell(row=15, column=6, value="=E15/C15").font = font_bold
    sheet_kpi.cell(row=15, column=7, value="=SUM(G13:G14)").font = font_bold
    sheet_kpi.cell(row=15, column=8, value="=SUM(H13:H14)").font = font_bold
    sheet_kpi.cell(row=15, column=9, value="=AVERAGE(I13:I14)").font = font_bold

    for c in range(2, 10):
        total_cell = sheet_kpi.cell(row=15, column=c)
        total_cell.border = total_border
        if c in [3, 4, 5]:
            total_cell.number_format = "#,##0"
        elif c == 6:
            total_cell.number_format = "0.0%"
        elif c in [7, 8]:
            total_cell.number_format = "$#,##0"
        elif c == 9:
            total_cell.number_format = "$#,##0.00"

    # -------------------------------------------------------------------------
    # Sheet 2: Lead Time Sensitivity Table
    # -------------------------------------------------------------------------
    sheet_lead = workbook.create_sheet(title="Lead Time Sensitivity")
    sheet_lead.views.sheetView[0].showGridLines = True

    sheet_lead["A1"].value = "Cancellation Risk by Booking Lead-Time Window"
    sheet_lead["A1"].font = font_section

    lead_headers = [
        "Lead Time Bucket", "Total Reservations", "Cancellations",
        "Cancellation Rate %", "Average ADR", "Lost Booking Revenue", "Realized Revenue"
    ]
    for column_index, header_text in enumerate(lead_headers, start=1):
        cell = sheet_lead.cell(row=3, column=column_index, value=header_text)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center")

    lead_rows = [
        ("1. Last Minute (0-7 Days)", 25480, 3560, "=C4/B4", 98.40, 680200, 4820100),
        ("2. Short Notice (8-30 Days)", 22150, 6820, "=C5/B5", 102.10, 1420500, 3750400),
        ("3. Moderate Advance (31-90 Days)", 31420, 12890, "=C6/B6", 104.50, 3180400, 4920800),
        ("4. Long Advance (91-180 Days)", 22890, 11450, "=C7/B7", 101.80, 2980100, 3120600),
        ("5. Early Bird (>180 Days)", 17450, 9504, "=C8/B8", 96.20, 2962420, 1807330)
    ]

    for row_idx, lead_data in enumerate(lead_rows, start=4):
        for col_idx, cell_value in enumerate(lead_data, start=1):
            cell = sheet_lead.cell(row=row_idx, column=col_idx, value=cell_value)
            cell.font = font_cell
            cell.border = thin_border
            if col_idx in [2, 3]:
                cell.number_format = "#,##0"
            elif col_idx == 4:
                cell.number_format = "0.0%"
                # Highlight buckets where cancellation rate exceeds 40%
                if row_idx >= 6:
                    cell.fill = fill_alert
            elif col_idx == 5:
                cell.number_format = "$#,##0.00"
            elif col_idx in [6, 7]:
                cell.number_format = "$#,##0"

    # -------------------------------------------------------------------------
    # Sheet 3: Monthly Overbooking Buffer Strategy
    # -------------------------------------------------------------------------
    sheet_ob = workbook.create_sheet(title="Overbooking Strategy")
    sheet_ob.views.sheetView[0].showGridLines = True

    sheet_ob["A1"].value = "Monthly Cancellation Rates & Safe Overbooking Recommendations"
    sheet_ob["A1"].font = font_section

    ob_headers = [
        "Month", "City Hotel Cancellation Rate", "City Recommended Overbooking Buffer",
        "Resort Hotel Cancellation Rate", "Resort Recommended Overbooking Buffer"
    ]
    for column_index, header_text in enumerate(ob_headers, start=1):
        cell = sheet_ob.cell(row=3, column=column_index, value=header_text)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center")

    monthly_data = [
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

    for row_idx, month_values in enumerate(monthly_data, start=4):
        for col_idx, cell_value in enumerate(month_values, start=1):
            cell = sheet_ob.cell(row=row_idx, column=col_idx, value=cell_value)
            cell.font = font_cell
            cell.border = thin_border
            if col_idx >= 2:
                cell.number_format = "0.0%"

    # Auto-adjust column widths across all sheets
    for ws in workbook.worksheets:
        for column in ws.columns:
            max_length = max(len(str(c.value or '')) for c in column)
            column_letter = get_column_letter(column[0].column)
            ws.column_dimensions[column_letter].width = max(max_length + 3, 14)

    workbook.save(OUTPUT_WORKBOOK_PATH)
    print(f"Excel financial model saved successfully to: {OUTPUT_WORKBOOK_PATH}")


if __name__ == "__main__":
    create_executive_excel_model()
