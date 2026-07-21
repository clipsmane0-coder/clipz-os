"""Development seed data command.

Usage:
    PYTHONPATH=. python -m app.utilities.seed
"""

import asyncio
from datetime import datetime, timezone, timedelta

from app.db.session import async_session
from app.models import (
    Profile, Source, Candidate, CandidateScore, Job, Notification,
    SystemSetting, ProfileSetting, ProfilePlatform, ProfileSource, AuditLog,
)
from app.models.models import gen_uuid


def iso(offset_days=0, offset_hours=0):
    d = datetime.now(timezone.utc) + timedelta(days=offset_days, hours=offset_hours)
    return d


async def seed():
    async with async_session() as session:
        # Clear existing data in dependency order
        for table in [AuditLog, ProfileSetting, SystemSetting, Notification,
                       Job, CandidateScore, Candidate, Source, ProfileSource,
                       ProfilePlatform, Profile]:
            await session.execute(table.__table__.delete())
        await session.commit()
        # === PROFILES ===
        profiles_data = [
            {"name": "Kai Cenat Clips", "slug": "kai-cenat-clips", "profile_type": "creator",
             "description": "High-energy streamer clips. Focus on reactions, arguments, and surprising moments.",
             "status": "active", "auto_approval_enabled": False},
            {"name": "Clip District", "slug": "clip-district", "profile_type": "general",
             "description": "Multi-creator clip network. Broad content from approved creators.",
             "status": "active", "auto_approval_enabled": False},
            {"name": "Tech Insights Daily", "slug": "tech-insights-daily", "profile_type": "topic",
             "description": "Technology commentary, product reviews, and industry analysis.",
             "status": "active", "auto_approval_enabled": True},
            {"name": "Comedy Hub", "slug": "comedy-hub", "profile_type": "topic",
             "description": "Stand-up clips, podcast comedy moments, and funny interviews.",
             "status": "active", "auto_approval_enabled": False},
            {"name": "Manual Uploads", "slug": "manual-uploads", "profile_type": "manual",
             "description": "Manually curated content.",
             "status": "active", "auto_approval_enabled": False},
            {"name": "Football Highlights", "slug": "football-highlights", "profile_type": "topic",
             "description": "Football match highlights.",
             "status": "paused", "auto_approval_enabled": False},
        ]
        profiles = {}
        for data in profiles_data:
            p = Profile(id=gen_uuid(), **data, created_at=iso(-90), updated_at=iso(-1))
            session.add(p)
            profiles[p.slug] = p
        await session.flush()

        # === SOURCES ===
        sources_data = [
            {"title": "Kai Cenat — Epic Rage Moment", "profile_id": profiles["kai-cenat-clips"].id,
             "duration_ms": 7200000, "status": "completed"},
            {"title": "Kai Cenat — Guest Podcast Episode", "profile_id": profiles["kai-cenat-clips"].id,
             "duration_ms": 10800000, "status": "completed"},
            {"title": "Gaming Tournament Finals", "profile_id": profiles["clip-district"].id,
             "duration_ms": 14400000, "status": "analyzing"},
            {"title": "Creator Collab Interview", "profile_id": profiles["clip-district"].id,
             "duration_ms": 4320000, "status": "transcribing"},
            {"title": "Tech Review — New Phone Deep Dive", "profile_id": profiles["tech-insights-daily"].id,
             "duration_ms": 2700000, "status": "candidates_ready"},
            {"title": "AI Chip Market Analysis", "profile_id": profiles["tech-insights-daily"].id,
             "duration_ms": 3480000, "status": "completed"},
            {"title": "Stand-Up Special", "profile_id": profiles["comedy-hub"].id,
             "duration_ms": 3300000, "status": "completed"},
            {"title": "Late Night Comedy Podcast", "profile_id": profiles["comedy-hub"].id,
             "duration_ms": 7200000, "status": "needs_review"},
            {"title": "Personal Vacation Vlog", "profile_id": profiles["manual-uploads"].id,
             "duration_ms": 1320000, "status": "completed"},
            {"title": "Charity Livestream (corrupted)", "profile_id": profiles["clip-district"].id,
             "duration_ms": 43200000, "status": "failed", "error_code": "SOURCE_UNREADABLE",
             "error_message": "File appears corrupted after byte 2.3 GB"},
        ]
        created_sources = []
        for data in sources_data:
            s = Source(id=gen_uuid(), source_type="upload", **data,
                       width=1920, height=1080, frame_rate=30.0, codec="h264",
                       file_size_bytes=1200000000, language="en",
                       rights_status="creator_approved",
                       imported_at=iso(-3), created_at=iso(-3), updated_at=iso(-1))
            session.add(s)
            created_sources.append(s)
        await session.flush()

        # === CANDIDATES ===
        hooks = [
            "You won't believe what happened next...",
            "This is the greatest moment of my career.",
            "Wait, that's actually insane.",
            "I never thought this would work.",
            "This changed EVERYTHING.",
        ]
        candidates_list = []
        for i, src in enumerate(created_sources[:6]):
            for j in range(3):
                c = Candidate(
                    id=gen_uuid(),
                    source_id=src.id,
                    profile_id=src.profile_id,
                    start_ms=j * 180000,
                    end_ms=(j * 180000) + 30000,
                    duration_ms=30000,
                    title=f"{src.title[:40]} — Clip {j + 1}",
                    hook_text=hooks[(i + j) % len(hooks)],
                    selection_reason="Strong hook with immediate payoff",
                    overall_score=55 + ((i * 13 + j * 7) % 40),
                    crop_confidence=0.75, audio_quality_score=0.85,
                    visual_quality_score=0.80, duplicate_risk=float((i * j) % 40),
                    safety_status="safe", rights_status="creator_approved",
                    approval_status="pending",
                    recommended_platform=["tiktok", "instagram", "youtube", "threads"][i % 4],
                    created_at=iso(-3, -i * 2), updated_at=iso(-1),
                )
                session.add(c)
                candidates_list.append(c)
        await session.flush()

        # === CANDIDATE SCORES ===
        for c in candidates_list:
            signals = [
                ("hook_strength", 20.0), ("emotional_intensity", 15.0),
                ("profile_match", 18.0), ("payoff_strength", 12.0),
                ("novelty", 10.0), ("visual_activity", 8.0),
            ]
            for name, weight in signals:
                raw = 50 + ((hash(c.id + name) % 400) / 10)
                norm = raw / 100
                cs = CandidateScore(
                    id=gen_uuid(),
                    candidate_id=c.id,
                    signal_name=name,
                    raw_value=raw,
                    normalized_value=norm,
                    weight=weight / 100,
                    weighted_score=norm * (weight / 100) * 100,
                    explanation=f"{name.replace('_', ' ')} — based on model analysis",
                    created_at=c.created_at,
                )
                session.add(cs)

        # === JOBS ===
        job_defs = [
            {"job_type": "render_clip", "entity_type": "candidate",
             "profile_id": profiles["kai-cenat-clips"].id, "status": "running",
             "progress_percent": 67, "priority": "high"},
            {"job_type": "render_clip", "entity_type": "candidate",
             "profile_id": profiles["kai-cenat-clips"].id, "status": "running",
             "progress_percent": 34, "priority": "normal"},
            {"job_type": "render_clip", "entity_type": "candidate",
             "profile_id": profiles["tech-insights-daily"].id, "status": "queued",
             "progress_percent": 0, "priority": "low"},
            {"job_type": "transcribe", "entity_type": "source",
             "profile_id": profiles["clip-district"].id, "status": "running",
             "progress_percent": 78, "priority": "normal"},
            {"job_type": "analyze_source", "entity_type": "source",
             "profile_id": profiles["clip-district"].id, "status": "running",
             "progress_percent": 45, "priority": "high"},
            {"job_type": "render_clip", "entity_type": "candidate",
             "profile_id": profiles["comedy-hub"].id, "status": "completed",
             "progress_percent": 100, "priority": "normal"},
            {"job_type": "render_clip", "entity_type": "candidate",
             "profile_id": profiles["clip-district"].id, "status": "failed",
             "progress_percent": 42, "priority": "high",
             "error_code": "RENDER_GPU_UNAVAILABLE",
             "error_message": "GPU memory allocation failed.",
             "attempts": 3, "max_attempts": 3, "retryable": False},
        ]
        for jd in job_defs:
            j = Job(
                id=gen_uuid(),
                entity_id="seed-entity",
                payload_json={"seed": True},
                **jd,
                created_at=iso(-1), updated_at=iso(0, -0.1),
            )
            session.add(j)

        # === NOTIFICATIONS ===
        notif_data = [
            ("action_required", "Candidates ready", "14 new candidates need review.", "source"),
            ("success", "Render complete", "Clip rendered successfully (28 MB).", "candidate"),
            ("error", "Render failed", "GPU memory allocation failed.", "candidate"),
            ("warning", "Storage nearly full", "Storage at 74%. Consider archiving.", None),
            ("informational", "Processing complete", "11 candidates generated.", "source"),
        ]
        for ntype, title, msg, etype in notif_data:
            n = Notification(
                id=gen_uuid(), type=ntype, title=title, message=msg,
                entity_type=etype, is_read=False,
                created_at=iso(-1),
            )
            session.add(n)

        # === SYSTEM SETTINGS ===
        default_settings = {
            "max_parallel_jobs": ("4", "number"),
            "gpu_enabled": ("true", "boolean"),
            "default_transcription_model": ("large-v3", "string"),
            "safety_threshold": ("0.5", "number"),
            "duplicate_threshold": ("0.7", "number"),
        }
        for key, (value, vtype) in default_settings.items():
            ss = SystemSetting(
                id=gen_uuid(), key=key, value=value,
                value_type=vtype, description=f"System setting: {key}",
                updated_at=iso(-1),
            )
            session.add(ss)

        await session.commit()
        print("Seed complete:")
        print(f"  Profiles: {len(profiles_data)}")
        print(f"  Sources: {len(sources_data)}")
        print(f"  Candidates: {len(candidates_list)}")
        print(f"  Candidate Scores: {len(candidates_list) * 6}")
        print(f"  Jobs: {len(job_defs)}")
        print(f"  Notifications: {len(notif_data)}")
        print(f"  Settings: {len(default_settings)}")


if __name__ == "__main__":
    asyncio.run(seed())