from typing import Optional, List, Tuple
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Profile, Source, Candidate, Job,
    Notification, SystemSetting, ProfileSetting, User, Session,
)
from app.models.models import utcnow, gen_uuid


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


# ============================================================
# USER REPOSITORY
# ============================================================
class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


# ============================================================
# PROFILE REPOSITORY
# ============================================================
class ProfileRepository(BaseRepository):
    async def list(self, user_id: str, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   profile_type: Optional[str] = None) -> Tuple[List[Profile], int]:
        query = select(Profile).where(Profile.user_id == user_id)
        if status:
            query = query.where(Profile.status == status)
        if profile_type:
            query = query.where(Profile.profile_type == profile_type)
        total_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_q)).scalar() or 0
        query = query.order_by(Profile.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, profile_id: str, user_id: Optional[str] = None) -> Optional[Profile]:
        query = select(Profile).where(Profile.id == profile_id)
        if user_id:
            query = query.where(Profile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, user_id: str) -> Optional[Profile]:
        result = await self.session.execute(
            select(Profile).where(Profile.slug == slug, Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Profile:
        profile = Profile(id=gen_uuid(), **data)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update(self, profile_id: str, user_id: str, data: dict) -> Optional[Profile]:
        profile = await self.get_by_id(profile_id, user_id)
        if not profile:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        profile.updated_at = utcnow()
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def delete(self, profile_id: str, user_id: str) -> bool:
        profile = await self.get_by_id(profile_id, user_id)
        if not profile:
            return False
        await self.session.delete(profile)
        await self.session.commit()
        return True


# ============================================================
# SOURCE REPOSITORY
# ============================================================
class SourceRepository(BaseRepository):
    async def list(self, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   profile_id: Optional[str] = None,
                   user_id: Optional[str] = None) -> Tuple[List[Source], int]:
        query = select(Source)
        if profile_id:
            query = query.where(Source.profile_id == profile_id)
        if user_id:
            # Scope sources to profiles owned by the user
            query = query.join(Profile, Source.profile_id == Profile.id).where(Profile.user_id == user_id)
        if status:
            query = query.where(Source.status == status)
        total_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_q)).scalar() or 0
        query = query.order_by(Source.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, source_id: str, user_id: Optional[str] = None) -> Optional[Source]:
        query = select(Source).where(Source.id == source_id)
        if user_id:
            query = query.join(Profile, Source.profile_id == Profile.id).where(Profile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Source:
        source = Source(id=gen_uuid(), **data)
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source

    async def update(self, source_id: str, data: dict, user_id: Optional[str] = None) -> Optional[Source]:
        source = await self.get_by_id(source_id, user_id)
        if not source:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(source, key, value)
        source.updated_at = utcnow()
        await self.session.commit()
        await self.session.refresh(source)
        return source


# ============================================================
# CANDIDATE REPOSITORY
# ============================================================
class CandidateRepository(BaseRepository):
    async def list(self, page: int = 1, page_size: int = 25,
                   approval_status: Optional[str] = None,
                   profile_id: Optional[str] = None,
                   source_id: Optional[str] = None,
                   min_score: Optional[float] = None,
                   user_id: Optional[str] = None) -> Tuple[List[Candidate], int]:
        query = select(Candidate)
        if approval_status:
            query = query.where(Candidate.approval_status == approval_status)
        if profile_id:
            query = query.where(Candidate.profile_id == profile_id)
        if source_id:
            query = query.where(Candidate.source_id == source_id)
        if min_score is not None:
            query = query.where(Candidate.overall_score >= min_score)
        if user_id:
            query = query.join(Profile, Candidate.profile_id == Profile.id).where(Profile.user_id == user_id)
        total_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_q)).scalar() or 0
        query = query.order_by(Candidate.overall_score.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, candidate_id: str, user_id: Optional[str] = None) -> Optional[Candidate]:
        query = select(Candidate).where(Candidate.id == candidate_id)
        if user_id:
            query = query.join(Profile, Candidate.profile_id == Profile.id).where(Profile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Candidate:
        candidate = Candidate(id=gen_uuid(), **data)
        self.session.add(candidate)
        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate

    async def update(self, candidate_id: str, data: dict, user_id: Optional[str] = None) -> Optional[Candidate]:
        candidate = await self.get_by_id(candidate_id, user_id)
        if not candidate:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(candidate, key, value)
        candidate.updated_at = utcnow()
        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate


# ============================================================
# JOB REPOSITORY
# ============================================================
class JobRepository(BaseRepository):
    async def list(self, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   job_type: Optional[str] = None,
                   profile_id: Optional[str] = None,
                   user_id: Optional[str] = None) -> Tuple[List[Job], int]:
        query = select(Job)
        if status:
            query = query.where(Job.status == status)
        if job_type:
            query = query.where(Job.job_type == job_type)
        if profile_id:
            query = query.where(Job.profile_id == profile_id)
        if user_id:
            query = query.join(Profile, Job.profile_id == Profile.id).where(Profile.user_id == user_id)
        total_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_q)).scalar() or 0
        query = query.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, job_id: str, user_id: Optional[str] = None) -> Optional[Job]:
        query = select(Job).where(Job.id == job_id)
        if user_id:
            query = query.join(Profile, Job.profile_id == Profile.id).where(Profile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Job:
        job = Job(id=gen_uuid(), **data)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update(self, job_id: str, data: dict, user_id: Optional[str] = None) -> Optional[Job]:
        job = await self.get_by_id(job_id, user_id)
        if not job:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(job, key, value)
        await self.session.commit()
        await self.session.refresh(job)
        return job


# ============================================================
# NOTIFICATION REPOSITORY
# ============================================================
class NotificationRepository(BaseRepository):
    async def list(self, page: int = 1, page_size: int = 25,
                   unread_only: bool = False,
                   user_id: Optional[str] = None,
                   profile_id: Optional[str] = None) -> Tuple[List[Notification], int]:
        query = select(Notification)
        if unread_only:
            query = query.where(Notification.is_read == False)
        if profile_id:
            query = query.where(Notification.profile_id == profile_id)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        total_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_q)).scalar() or 0
        query = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def mark_read(self, notification_id: str, user_id: Optional[str] = None) -> bool:
        query = update(Notification).where(Notification.id == notification_id)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        result = await self.session.execute(query.values(is_read=True))
        await self.session.commit()
        return result.rowcount > 0


# ============================================================
# SETTINGS REPOSITORY
# ============================================================
class SettingsRepository(BaseRepository):
    async def get_all(self) -> List[SystemSetting]:
        result = await self.session.execute(select(SystemSetting))
        return list(result.scalars().all())

    async def get(self, key: str) -> Optional[SystemSetting]:
        result = await self.session.execute(select(SystemSetting).where(SystemSetting.key == key))
        return result.scalar_one_or_none()

    async def set(self, key: str, value: str) -> SystemSetting:
        setting = await self.get(key)
        if setting:
            setting.value = value
            setting.updated_at = utcnow()
        else:
            setting = SystemSetting(id=gen_uuid(), key=key, value=value)
            self.session.add(setting)
        await self.session.commit()
        await self.session.refresh(setting)
        return setting

    async def get_profile_settings(self, profile_id: str, user_id: Optional[str] = None) -> List[ProfileSetting]:
        # Verify profile belongs to user if user_id provided
        if user_id:
            result = await self.session.execute(
                select(Profile).where(Profile.id == profile_id, Profile.user_id == user_id)
            )
            if not result.scalar_one_or_none():
                return []
        result = await self.session.execute(
            select(ProfileSetting).where(ProfileSetting.profile_id == profile_id)
        )
        return list(result.scalars().all())

    async def set_profile_setting(self, profile_id: str, key: str, value: str, user_id: Optional[str] = None) -> Optional[ProfileSetting]:
        # Verify profile belongs to user if user_id provided
        if user_id:
            result = await self.session.execute(
                select(Profile).where(Profile.id == profile_id, Profile.user_id == user_id)
            )
            if not result.scalar_one_or_none():
                return None
        result = await self.session.execute(
            select(ProfileSetting).where(
                ProfileSetting.profile_id == profile_id,
                ProfileSetting.key == key,
            )
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            setting.updated_at = utcnow()
        else:
            setting = ProfileSetting(id=gen_uuid(), profile_id=profile_id, key=key, value=value)
            self.session.add(setting)
        await self.session.commit()
        await self.session.refresh(setting)
        return setting