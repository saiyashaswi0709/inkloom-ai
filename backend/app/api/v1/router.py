from fastapi import APIRouter
from app.api.v1 import (
    auth, organisations, guidelines, facts, rules,
    submissions, analysis, corrections, reviews, analytics,
    invitations
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organisations.router)
api_router.include_router(invitations.router)
api_router.include_router(guidelines.router)
api_router.include_router(facts.router)
api_router.include_router(rules.router)
api_router.include_router(submissions.router)
api_router.include_router(analysis.router)
api_router.include_router(corrections.router)
api_router.include_router(reviews.router)
api_router.include_router(analytics.router)
