"""Source Ingestion Workflow.

Coordinates profile validation, upload validation, checksum calculation,
duplicate detection, storage write, source record creation, media inspection,
thumbnail extraction, and analysis job creation.

Compensates for partial failure:
- If DB creation fails after storage, removes stored file.
- If storage fails, does not create source record.
- If inspection fails, marks source as failed and preserves diagnostics.
"""



class SourceIngestionWorkflow:
    """Orchestrates the full source ingestion pipeline."""

    async def run(self):
        """Execute the ingestion workflow.

        Future steps (Phase 4):
        1. Validate profile exists
        2. Validate upload (size, type, MIME)
        3. Calculate SHA-256 checksum
        4. Check for duplicate
        5. Write file to storage
        6. Create source database record
        7. Inspect media with FFprobe
        8. Extract thumbnail
        9. Update source metadata
        10. Create analysis job
        11. Return completed source + job
        """
        raise NotImplementedError("Full ingestion workflow in Phase 4")


class SourceValidationWorkflow:
    """Validates a source before ingestion."""

    async def validate(self):
        raise NotImplementedError("Phase 4")


class SourceInspectionWorkflow:
    """Inspects media metadata after storage."""

    async def inspect(self):
        raise NotImplementedError("Phase 4")


class AnalysisJobCreationWorkflow:
    """Creates an analysis job after successful inspection."""

    async def create(self):
        raise NotImplementedError("Phase 4")