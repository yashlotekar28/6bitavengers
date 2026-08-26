"""
Async Celery task: runs the full portal verification pipeline for a bidder.
Called by POST /api/verify/{bidder_id} — returns a Celery task_id immediately,
and the React frontend polls GET /api/verify/status/{task_id} to stream progress.

Person A (task scheduling + DB writes) + Person B (OCR + AI recommendation)
"""
import asyncio
from app.tasks.celery_app import celery


@celery.task(bind=True, name="run_verification_pipeline", max_retries=2)
def run_verification_pipeline(self, bidder_id: str, tender_id: str, scenario_type: str = "apex"):
    """
    Background job that:
      1. Runs all portal adapters concurrently (GST, PAN, Udyam, EPFO, MCA21, Debarment)
      2. Triggers OCR extraction on uploaded documents (Person B)
      3. Cross-verifies OCR output vs portal records
      4. Evaluates YAML rules engine
      5. Gets AI recommendation (Claude/GPT structured output)
      6. Computes compliance score + trust score
      7. Writes all results to PostgreSQL
      8. Pushes a WebSocket notification to the frontend (Person C)
    """
    try:
        # Update task state so frontend polling sees progress
        self.update_state(state="STARTED", meta={"step": "Initialising verification pipeline", "progress": 0})

        # Run the async pipeline in a new event loop (Celery workers are sync)
        result = asyncio.get_event_loop().run_until_complete(
            _run_pipeline_async(self, bidder_id, tender_id, scenario_type)
        )
        return result

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


async def _run_pipeline_async(task, bidder_id: str, tender_id: str, scenario_type: str):
    """Inner async pipeline — runs all steps and returns a summary dict."""

    # Lazy imports to avoid circular deps at module load time
    from app.data.demo_scenarios import DEMO_BIDDERS_SEED, build_bidder_from_seed
    from app.main import run_full_pipeline_for_bidder
    from app.services.audit_service import AuditService

    # Step 1-2: Load or fetch bidder data
    task.update_state(state="PROGRESS", meta={"step": "Fetching bidder data from adapters", "progress": 15})
    seed = next((s for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder_id), None)
    if not seed:
        raise ValueError(f"Bidder {bidder_id} not found in seed / database")
    bidder = build_bidder_from_seed(seed)

    # Step 3-4: Cross-verification + rules engine
    task.update_state(state="PROGRESS", meta={"step": "Running cross-verification & rules engine", "progress": 45})

    # Step 5-7: AI recommendation + scoring
    task.update_state(state="PROGRESS", meta={"step": "Computing AI recommendation & compliance score", "progress": 70})
    updated_bidder = await run_full_pipeline_for_bidder(bidder, scenario_type=scenario_type)

    # Step 8: Audit trail
    task.update_state(state="PROGRESS", meta={"step": "Writing audit trail to PostgreSQL", "progress": 90})
    AuditService.log(
        bidder_id=bidder_id,
        event_type="ASYNC_PIPELINE_COMPLETE",
        details={
            "compliance_score": updated_bidder.compliance_score.score,
            "risk_level": updated_bidder.compliance_score.risk_level.value,
            "trust_score": updated_bidder.longitudinal_trust_score.score,
            "recommendation": updated_bidder.ai_recommendation.recommended_action,
        }
    )

    return {
        "bidder_id": bidder_id,
        "company_name": updated_bidder.company_name,
        "compliance_score": updated_bidder.compliance_score.score,
        "risk_level": updated_bidder.compliance_score.risk_level.value,
        "trust_score": updated_bidder.longitudinal_trust_score.score,
        "recommendation": updated_bidder.ai_recommendation.recommended_action,
        "status": "COMPLETED",
    }
