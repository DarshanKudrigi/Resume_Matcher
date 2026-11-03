import sys
import os
import json
import asyncio
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure agent site-packages is in path
AGENT_DIR = BASE_DIR.parent / "job-application-agent"
AGENT_SITE_PACKAGES = AGENT_DIR / "venv" / "Lib" / "site-packages"
if AGENT_SITE_PACKAGES.exists() and str(AGENT_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(AGENT_SITE_PACKAGES))
if AGENT_DIR.exists() and str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from app.schemas.recommendation import JobRecommendationRequest
from app.services.job_recommendation_service import JobRecommendationService

async def test_stream():
    print("Testing stream_recommendations with resume...")
    req = JobRecommendationRequest(
        desired_role="Software Engineer",
        location="Bengaluru",
        platforms=[], # empty platforms for instant unit validation of the pipeline without network delays
        resume_data={
            "personalInfo": {"fullName": "Darshan Candidate"},
            "skills": {
                "languages": ["Python", "JavaScript"],
                "frameworks": ["FastAPI", "React"]
            }
        }
    )

    events_received = []
    async for raw_chunk in JobRecommendationService.stream_recommendations(req):
        raw_chunk = raw_chunk.strip()
        if raw_chunk.startswith("data: "):
            data = json.loads(raw_chunk[6:])
            events_received.append(data)
            print(f"  Step {data.get('step')}: [{data.get('type')}] status={data.get('status')} -> {data.get('message')}")

    steps = [e.get("step") for e in events_received]
    print(f"\nReceived {len(events_received)} event(s) across steps: {steps}")
    
    assert 1 in steps, "Step 1 (Resume Processing) must be present"
    assert 6 in steps, "Step 6 (Completion) must be present"
    
    complete_event = next(e for e in events_received if e.get("step") == 6)
    assert complete_event.get("status") == "completed", "Final event status must be completed"
    print("\n[PASS] Stream recommendations event flow verified successfully!")

if __name__ == "__main__":
    asyncio.run(test_stream())

