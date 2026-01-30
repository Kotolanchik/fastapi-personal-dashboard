from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import analytics, schemas
from ..deps import get_db_session

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/correlations", response_model=schemas.CorrelationsResponse)
def correlations(db: Session = Depends(get_db_session)):
    df = analytics.build_daily_dataframe(db)
    correlations_data = analytics.compute_correlations(df)
    return {"correlations": correlations_data}


@router.get("/insights", response_model=schemas.InsightsResponse)
def insights(db: Session = Depends(get_db_session)):
    return analytics.insights_payload(db)
