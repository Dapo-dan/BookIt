from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.core.dependencies import get_current_user, require_role
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate
from app.models.review import Review
from app.models.booking import Booking, BookingStatus

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewOut, status_code=201)
async def create_review(
    data: ReviewCreate, 
    payload=Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    # Get the booking and verify it belongs to the user and is completed
    booking = (await session.execute(
        select(Booking).where(Booking.id == data.booking_id)
    )).scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Not your booking")
    
    if booking.status != BookingStatus.completed:
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
    
    # Check if review already exists
    existing_review = (await session.execute(
        select(Review).where(Review.booking_id == data.booking_id)
    )).scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(status_code=409, detail="Review already exists for this booking")
    
    # Create the review
    review = Review(
        booking_id=data.booking_id,
        rating=data.rating,
        comment=data.comment
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)
    
    return ReviewOut(
        id=review.id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    )

@router.get("/services/{service_id}", response_model=list[ReviewOut])
async def get_service_reviews(
    service_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Get all reviews for bookings of this service
    reviews = (await session.execute(
        select(Review)
        .join(Booking, Review.booking_id == Booking.id)
        .where(Booking.service_id == service_id)
        .order_by(Review.created_at.desc())
    )).scalars().all()
    
    return [
        ReviewOut(
            id=r.id,
            booking_id=r.booking_id,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at
        ) for r in reviews
    ]

@router.patch("/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    payload=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    review = (await session.execute(
        select(Review).where(Review.id == review_id)
    )).scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns the review (via booking)
    booking = (await session.execute(
        select(Booking).where(Booking.id == review.booking_id)
    )).scalar_one()
    
    if booking.user_id != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Not your review")
    
    # Update the review
    if data.rating is not None:
        review.rating = data.rating
    if data.comment is not None:
        review.comment = data.comment
    
    await session.commit()
    await session.refresh(review)
    
    return ReviewOut(
        id=review.id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    )

@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    payload=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    review = (await session.execute(
        select(Review).where(Review.id == review_id)
    )).scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns the review or is admin
    booking = (await session.execute(
        select(Booking).where(Booking.id == review.booking_id)
    )).scalar_one()
    
    is_owner = booking.user_id == int(payload["sub"])
    is_admin = payload.get("role") == "admin"
    
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await session.delete(review)
    await session.commit()
    return
