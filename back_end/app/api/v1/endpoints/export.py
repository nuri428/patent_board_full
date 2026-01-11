from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.crud import get_patent_crud
from app.schemas import Patent
from typing import List
import csv
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter

router = APIRouter()


@router.get("/patents/csv")
async def export_patents_csv(db: AsyncSession = Depends(get_db)):
    patent_crud = get_patent_crud(db)
    patents = await patent_crud.get_all(skip=0, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Patent ID",
            "Title",
            "Abstract",
            "Status",
            "Assignee",
            "Inventors",
            "Filing Date",
            "Created At",
            "Updated At",
        ]
    )

    for patent in patents:
        writer.writerow(
            [
                patent.patent_id,
                patent.title,
                patent.abstract,
                patent.status,
                patent.assignee or "",
                "; ".join(patent.inventors or []),
                patent.filing_date.isoformat() if patent.filing_date else "",
                patent.created_at.isoformat() if patent.created_at else "",
                patent.updated_at.isoformat() if patent.updated_at else "",
            ]
        )

    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=patents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/patents/excel")
async def export_patents_excel(db: AsyncSession = Depends(get_db)):
    patent_crud = get_patent_crud(db)
    patents = await patent_crud.get_all(skip=0, limit=10000)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Patents")

    headers = [
        "Patent ID",
        "Title",
        "Abstract",
        "Status",
        "Assignee",
        "Inventors",
        "Filing Date",
        "Created At",
    ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header, workbook.add_format({"bold": True}))

    for row, patent in enumerate(patents, start=1):
        worksheet.write(row, 0, patent.patent_id)
        worksheet.write(row, 1, patent.title)
        worksheet.write(row, 2, patent.abstract)
        worksheet.write(row, 3, patent.status)
        worksheet.write(row, 4, patent.assignee or "")
        worksheet.write(row, 5, "; ".join(patent.inventors or []))
        worksheet.write(
            row,
            6,
            patent.filing_date.strftime("%Y-%m-%d") if patent.filing_date else "",
        )
        worksheet.write(
            row,
            7,
            patent.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if patent.created_at
            else "",
        )

    worksheet.set_column(0, 0, 15)
    worksheet.set_column(1, 1, 40)
    worksheet.set_column(2, 2, 50)
    worksheet.set_column(3, 3, 15)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 5, 40)
    worksheet.set_column(6, 7, 20)

    workbook.close()
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=patents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        },
    )


@router.get("/patents/pdf")
async def export_patents_pdf(db: AsyncSession = Depends(get_db)):
    patent_crud = get_patent_crud(db)
    patents = await patent_crud.get_all(skip=0, limit=100)
    patent_schemas = [Patent.model_validate(patent) for patent in patents]

    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    story.append(Paragraph("Patent Database Export", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style
        )
    )
    story.append(Spacer(1, 20))

    for patent in patent_schemas:
        story.append(Paragraph(f"Patent ID: {patent.patent_id}", heading_style))
        story.append(Paragraph(f"Title: {patent.title}", normal_style))
        story.append(Paragraph(f"Status: {patent.status}", normal_style))
        story.append(
            Paragraph(f"Assignee: {patent.assignee or 'Not specified'}", normal_style)
        )

        if patent.inventors:
            inventors_text = ", ".join(patent.inventors)
            story.append(Paragraph(f"Inventors: {inventors_text}", normal_style))

        if patent.filing_date:
            filing_text = patent.filing_date.strftime("%B %d, %Y")
            story.append(Paragraph(f"Filing Date: {filing_text}", normal_style))

        story.append(Paragraph("Abstract:", heading_style))
        story.append(Paragraph(patent.abstract, normal_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=patents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        },
    )


@router.get("/reports/csv")
async def export_reports_csv(db: AsyncSession = Depends(get_db)):
    from app.models import Report
    from sqlalchemy import select

    result = await db.execute(select(Report))
    reports = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Report ID", "Topic", "Report Type", "Patent Count", "Created At"])

    for report in reports:
        patent_count = (
            len(report.patent_ids)
            if hasattr(report, "patent_ids") and report.patent_ids
            else 0
        )
        writer.writerow(
            [
                report.id,
                report.topic,
                report.report_type,
                patent_count,
                report.created_at.isoformat() if report.created_at else "",
            ]
        )

    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/reports/pdf")
async def export_reports_pdf(db: AsyncSession = Depends(get_db)):
    from app.models import Report
    from sqlalchemy import select

    result = await db.execute(select(Report))
    reports = result.scalars().all()

    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    story.append(Paragraph("Reports Export", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style
        )
    )
    story.append(Spacer(1, 20))

    for report in reports:
        story.append(Paragraph(f"Report ID: {report.id}", heading_style))
        story.append(Paragraph(f"Topic: {report.topic}", normal_style))
        story.append(Paragraph(f"Type: {report.report_type}", normal_style))

        patent_count = (
            len(report.patent_ids)
            if hasattr(report, "patent_ids") and report.patent_ids
            else 0
        )
        story.append(Paragraph(f"Patents Analyzed: {patent_count}", normal_style))

        if report.created_at:
            created_text = report.created_at.strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Created: {created_text}", normal_style))

        story.append(Paragraph("Content:", heading_style))
        story.append(Paragraph(str(report.content)[:500] + "...", normal_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        },
    )


@router.post("/custom")
async def export_custom_data(export_config: dict, db: AsyncSession = Depends(get_db)):
    export_type = export_config.get("type", "csv")
    data_type = export_config.get("data_type", "patents")
    filters = export_config.get("filters", {})

    if data_type == "patents":
        from app.schemas import PatentSearch

        search_params = PatentSearch(
            limit=filters.get("limit", 1000),
            offset=filters.get("offset", 0),
            title=filters.get("title"),
            abstract=filters.get("abstract"),
            assignee=filters.get("assignee"),
            status=filters.get("status"),
            filing_date_from=datetime.fromisoformat(filters["filing_date_from"])
            if filters.get("filing_date_from")
            else None,
            filing_date_to=datetime.fromisoformat(filters["filing_date_to"])
            if filters.get("filing_date_to")
            else None,
        )

        patent_crud = get_patent_crud(db)
        patents, _ = await patent_crud.advanced_search(search_params)
        patent_schemas = [Patent.model_validate(patent) for patent in patents]

        if export_type == "json":
            json_data = [patent.model_dump() for patent in patent_schemas]
            return Response(
                content=json.dumps(json_data, indent=2, default=str),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=patents_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                },
            )
        elif export_type == "csv":
            return await export_patents_csv(db)
        elif export_type == "excel":
            return await export_patents_excel(db)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export type")

    else:
        raise HTTPException(status_code=400, detail="Unsupported data type")
