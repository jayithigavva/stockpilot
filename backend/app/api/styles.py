"""
Style management endpoints for footwear.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.inventory import Style
from app.api.schemas import StyleCreate, StyleResponse

router = APIRouter(prefix="/styles", tags=["styles"])


@router.get("", response_model=List[StyleResponse])
def list_styles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all styles for the user's brand."""
    styles = db.query(Style).filter(
        Style.brand_id == current_user.brand_id
    ).all()
    return styles


@router.post("", response_model=StyleResponse, status_code=status.HTTP_201_CREATED)
def create_style(
    style_data: StyleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new style."""
    # Check if style_code already exists for this brand
    existing = db.query(Style).filter(
        Style.brand_id == current_user.brand_id,
        Style.style_code == style_data.style_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Style code already exists for this brand"
        )
    
    # Create style
    style = Style(
        brand_id=current_user.brand_id,
        **style_data.dict()
    )
    
    db.add(style)
    db.commit()
    db.refresh(style)
    
    return style


@router.get("/{style_id}", response_model=StyleResponse)
def get_style(
    style_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific style."""
    style = db.query(Style).filter(
        Style.id == style_id,
        Style.brand_id == current_user.brand_id
    ).first()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found"
        )
    
    return style


@router.put("/{style_id}", response_model=StyleResponse)
def update_style(
    style_id: int,
    style_data: StyleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a style."""
    style = db.query(Style).filter(
        Style.id == style_id,
        Style.brand_id == current_user.brand_id
    ).first()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found"
        )
    
    # Check if style_code conflicts with another style
    if style_data.style_code != style.style_code:
        existing = db.query(Style).filter(
            Style.brand_id == current_user.brand_id,
            Style.style_code == style_data.style_code,
            Style.id != style_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Style code already exists for this brand"
            )
    
    # Update style
    for key, value in style_data.dict().items():
        setattr(style, key, value)
    
    db.commit()
    db.refresh(style)
    
    return style


@router.delete("/{style_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_style(
    style_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a style."""
    style = db.query(Style).filter(
        Style.id == style_id,
        Style.brand_id == current_user.brand_id
    ).first()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found"
        )
    
    db.delete(style)
    db.commit()
    
    return None

