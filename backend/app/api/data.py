"""
Data upload endpoints for sales history.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.inventory import Product, SalesHistory
from app.api.schemas import SalesDataUpload, SalesDataBulkUpload

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/sales/upload", status_code=status.HTTP_201_CREATED)
def upload_sales_data(
    data: SalesDataBulkUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload sales history data."""
    records = []
    
    for item in data.data:
        # Verify product belongs to brand
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.brand_id == current_user.brand_id
        ).first()
        
        if not product:
            continue  # Skip invalid products
        
        # Check if record already exists
        existing = db.query(SalesHistory).filter(
            SalesHistory.product_id == item.product_id,
            SalesHistory.date == item.date
        ).first()
        
        if existing:
            # Update existing
            existing.demand = item.demand
            if item.revenue is not None:
                existing.revenue = item.revenue
        else:
            # Create new
            sales_record = SalesHistory(
                product_id=item.product_id,
                date=item.date,
                demand=item.demand,
                revenue=item.revenue
            )
            db.add(sales_record)
            records.append(sales_record)
    
    db.commit()
    
    return {
        "message": f"Uploaded {len(records)} new records and updated existing ones",
        "records_created": len(records)
    }


@router.post("/sales/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_sales_csv(
    file: UploadFile = File(...),
    product_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload sales data from CSV file.
    
    CSV should have columns: date, demand (and optionally revenue)
    """
    if not product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id is required"
        )
    
    # Verify product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == current_user.brand_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Read CSV
    try:
        df = pd.read_csv(file.file)
        
        # Validate columns
        required_cols = ['date', 'demand']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV must have columns: {required_cols}"
            )
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Insert records
        records_created = 0
        for _, row in df.iterrows():
            existing = db.query(SalesHistory).filter(
                SalesHistory.product_id == product_id,
                SalesHistory.date == row['date']
            ).first()
            
            if existing:
                existing.demand = row['demand']
                if 'revenue' in df.columns:
                    existing.revenue = row.get('revenue')
            else:
                sales_record = SalesHistory(
                    product_id=product_id,
                    date=row['date'],
                    demand=row['demand'],
                    revenue=row.get('revenue')
                )
                db.add(sales_record)
                records_created += 1
        
        db.commit()
        
        return {
            "message": f"Uploaded {records_created} new records",
            "records_created": records_created,
            "total_rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}"
        )

