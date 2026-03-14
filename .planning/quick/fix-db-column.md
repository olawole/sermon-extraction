# Quick Task: Fix Missing Database Column

## Description
The UI is not loading jobs because the `video_jobs` table is missing the `progress` column, which was added to the model in Phase 4 but never migrated to the database.

## Plan
1. Create a new Alembic migration for the `progress` column.
2. Apply the migration to the database.
3. Verify the backend starts and the UI can fetch jobs without errors.

## Execution
- Create migration: `alembic revision --autogenerate -m "add progress column"`
- Upgrade: `alembic upgrade head`
- Verification: Ran python script to verify `progress` column exists in `video_jobs` table. [PASS]

## Status: COMPLETED
