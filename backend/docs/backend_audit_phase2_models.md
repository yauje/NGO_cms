# Backend Audit — Phase 2: Database Models Report

## 1. User Model (`app/db/models/user.py`)
**Status:** ✅ Well-structured  
**Highlights**
- `email` is unique and indexed — ✔️  
- Secure field naming (`hashed_password`) avoids leaks — ✔️  
- `last_token_issue` supports refresh-token revocation — ✔️  
- Proper relationships to `PageRevision`, `Media`, and `AuditLog` — ✔️  
- Uses async helper methods `get_by_email` and `create` — 👌  

**Suggestions**
- Add `nullable=False` to `last_token_issue` if you always initialize it.  
- Consider limiting `role` values via `Enum` for stricter validation.  



## 2. Page Model (`app/db/models/page.py`)
**Status:** ✅ Clean and efficient  
**Highlights**
- Fixed redundant index on `slug` — ✔️  
- Proper `created_at` / `updated_at` handling — ✔️  
- Relationships with `PageRevision` and `PageBlock` configured correctly — ✔️  
- Uses `lazy="selectin"` for better async performance — 👍  

**Suggestions**
- Consider adding a `ForeignKey` for author or editor if version ownership is needed later.  

---

## 3. PageBlock Model (`app/db/models/page_block.py`)
**Status:** ✅ Flexible and relationally sound  
**Highlights**
- Uses `JSON` for content — enables rich CMS blocks — ✔️  
- Proper cascading delete via `page_id` → `pages.id` — ✔️  
- Timestamps use `server_default=func.now()` — ✔️  
- Relationship to `User` as `creator` — clear data ownership — ✔️  

**Suggestions**
- Optional: rename `creator` → `created_by` for consistent naming with other models.  
- Ensure `content` default `{}` does not share mutable dict reference (better to use `default=dict`).  

---

## 4. PageRevision Model (`app/db/models/page_revision.py`)
**Status:** ✅ Consistent and performant  
**Highlights**
- Proper indexes for `page_id` + `status` — ✔️  
- Tracks `created_by_user_id` → `users.id` — ✔️  
- Supports versioned states (`draft`, `published`, `archived`) — ✔️  

**Suggestions**
- Enforce valid statuses via `Enum` or validation in schema.  

---

## 5. Media Model (`app/db/models/media.py`)
**Status:** ✅ Clear and minimal  
**Highlights**
- Tracks uploader, file metadata, and timestamps — ✔️  
- `uploaded_by_user_id` → `users.id` foreign key integrity — ✔️  

**Suggestions**
- Consider adding `is_deleted` flag or soft-delete policy for media cleanup.  
- Optional: include checksum/hash field for duplicate detection.  

---

## 6. SiteSetting Model (`app/db/models/site_setting.py`)
**Status:** ✅ Efficient key-value store  
**Highlights**
- Unique `key` field with explicit index — ✔️  
- Uses `Text` for flexible value storage — ✔️  

**Suggestions**
- You may later extend `value` to `JSON` if structured settings become common.  

---

## 7. AuditLog Model (`app/db/models/audit_log.py`)
**Status:** ✅ Secure and traceable  
**Highlights**
- Captures `user_id`, `action`, `resource_type`, `resource_id`, and timestamp — ✔️  
- Indexed by resource for fast lookup — ✔️  

**Suggestions**
- Optional: add `details` (JSON/Text) for contextual metadata (e.g., old vs new values).  
- Confirm audit writes occur automatically in CRUD layer for critical actions.  

---

## 8. `__init__.py` Integration
**Status:** ✅  
All models are properly imported and registered in `__all__`.  
No circular import risks detected.  

---

## Summary

| Category | Result |
|-----------|---------|
| **Primary Keys / Indexes** | ✅ All correctly defined |
| **Foreign Keys & Cascade Rules** | ✅ Consistent |
| **Relationships & back_populates** | ✅ Accurate |
| **Timestamps & Defaults** | ✅ UTC safe |
| **Sensitive Data Protection** | ✅ Handled properly |
| **Overall Schema Readiness** | ✅ Production-ready |



## Next Steps (Phase 2.1 → Phase 3 Preparation)
1. **Validate schema alignment** with Pydantic models (`app/schemas/`).  
2. **Check CRUD layer** (`app/crud/`) for consistent use of async sessions, transactions, and audit integration.  
3. **Document field mappings** in `backend_audit_phase2_models.md`.  
4. After confirmation, proceed to **Phase 3: API Route & Security Audit** (Auth, Permissions, CRUD endpoints).
