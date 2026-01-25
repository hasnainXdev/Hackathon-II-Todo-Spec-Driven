# Duplicate Table Definition Fix

## Issue
The application was experiencing the following error:
```
sqlalchemy.exc.InvalidRequestError: Table 'conversations' is already defined for this MetaData instance. Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
```

## Root Cause
The issue was caused by duplicate table definitions for 'conversations' and 'messages' in multiple locations:
1. `backend/models/message.py` contained Conversation and Message models
2. `backend/src/models/conversation.py` also contained Conversation and Message models
3. Both were being imported in different parts of the application, causing SQLAlchemy to register the same tables twice

## Solution Implemented

1. **Consolidated model imports** in `backend/models/__init__.py`:
   - Removed local Message/Conversation imports
   - Used only the src models to avoid duplication

2. **Updated alembic configuration** in `backend/alembic/env.py`:
   - Changed to import only from src models to avoid duplicates

3. **Fixed Task model relationships** in `backend/models/task.py`:
   - Used TYPE_CHECKING to handle cross-module imports
   - Updated relationship references to use full module paths

4. **Maintained backward compatibility** by ensuring all expected exports are available

## Files Modified
- `backend/alembic/env.py` - Fixed model imports for alembic
- `backend/models/__init__.py` - Consolidated model imports
- `backend/models/task.py` - Fixed cross-module relationship references
- Created `test_model_imports.py` - Test script to verify the fix

## Verification
The fix was verified using the test script `test_model_imports.py` which confirms that:
- All models can be imported without conflicts
- The TaskCreate model still works without requiring user_id in the request
- No duplicate table definitions occur