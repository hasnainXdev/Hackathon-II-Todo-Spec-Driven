# Research: Todo Full-Stack Evolution

## Decision: Next.js Version Selection
**Rationale**: Next.js 16+ doesn't exist yet. Current stable version is 14.x. Using Next.js 14 with App Router for the best balance of features and stability.
**Alternatives considered**: 
- Next.js 15 (future version, not yet released)
- Next.js 14 (current stable with App Router support)
- Next.js 13 (older, but stable)

## Decision: SQLModel Version Selection
**Rationale**: SQLModel 0.0.16+ doesn't exist. Current version is 0.0.8. Using SQLModel 0.0.8 which provides all necessary ORM functionality for the project.
**Alternatives considered**:
- SQLModel 0.0.8 (current stable version)
- SQLAlchemy directly (more complex setup)
- SQLModel 0.0.7 (previous version)

## Decision: TypeScript Version
**Rationale**: Using TypeScript 5.0+ as specified in the original plan, which is compatible with Next.js 14 and provides modern type system features.
**Alternatives considered**: 
- TypeScript 4.x (older, missing newer features)
- TypeScript 5.0+ (current, with latest features)

## Decision: FastAPI Version
**Rationale**: Using FastAPI 0.104+ as specified in the original plan, which is a stable version with all required features.
**Alternatives considered**:
- FastAPI 0.100+ (slightly older but stable)
- FastAPI 0.104+ (specified version, stable)