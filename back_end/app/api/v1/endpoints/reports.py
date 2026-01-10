from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_report():
    return {"message": "Generate report endpoint"}


@router.get("/{report_id}")
async def get_report(report_id: str):
    return {"message": f"Get report {report_id}"}


@router.get("/")
async def list_reports():
    return {"message": "List reports endpoint"}