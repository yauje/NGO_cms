# Backend Audit — Phase 2b: Pydantic Schemas Report

## 1. User Schemas (`app/schemas/user.py`)
**Status:** ✅ Well-aligned with model  
**Highlights**
- `UserBase` covers core attributes (email, role, is_active) — ✔️  
- `UserCreate` includes password, role optional with default `"public"` — ✔️  
- `UserUpdate` allows partial updates — ✔️  
- `UserRead` includes id and timestamps with `from_attributes=True` — ✔️  

**Suggestions**
- Consider adding password validation (min length, complexity) in `UserCreate`.  
- Optionally define `role` as `Literal["public","editor","admin"]` for stricter validation.  

---

## 2. Page Schemas (`app/schemas/page.py`)
**Status:** ✅ Correct and simple  
**Highlights**
- `PageBase` includes `slug`, `title`, `is_published` — ✔️  
- `PageCreate` inherits `PageBase` — ✔️  
- `PageUpdate` supports partial updates — ✔️  
- `PageRead` includes id, created_at, updated_at with `from_attributes=True` — ✔️  

**Suggestions**
- Validate `slug` for allowed characters (e.g., regex).  

---

## 3. PageBlock Schemas (`app/schemas/page_block.py`)
**Status:** ✅ Flexible and descriptive  
**Highlights**
- `PageBlockBase` includes `page_id`, `type`, `content`, `order` — ✔️  
- `PageBlockCreate` adds `created_by_id` — ✔️  
- `PageBlockUpdate` supports optional partial updates — ✔️  
- `PageBlockRead` adds id, created_by_id, timestamps — ✔️  

**Suggestions**
- Ensure `content` JSON is validated (nested fields if necessary).  

---

## 4. PageRevision Schemas (`app/schemas/page_revision.py`)
**Status:** ✅ Matches model  
**Highlights**
- `PageRevisionBase` with `content` field — ✔️  
- `PageRevisionCreate` adds `page_id` and `created_by_id` — ✔️  
- `PageRevisionRead` includes id, page_id, created_by_id, created_at — ✔️  

**Suggestions**
- Validate `status` via enum if included in CRUD layer.  

---

## 5. Media Schemas (`app/schemas/media.py`)
**Status:** ✅ Reflects model accurately  
**Highlights**
- `MediaBase` includes `filename`, `filepath`, `mimetype` — ✔️  
- `MediaCreate` adds `uploaded_by_id` — ✔️  
- `MediaRead` adds id, uploaded_by_id, uploaded_at — ✔️  

**Suggestions**
- Consider file size field if API responses need it.  

---

## 6. SiteSetting Schemas (`app/schemas/site_setting.py`)
**Status:** ✅ Clear and safe  
**Highlights**
- `SiteSettingBase` with `value` field — ✔️  
- `SiteSettingCreate` adds `key` for creation — ✔️  
- `SiteSettingUpdate` only updates `value` — ✔️  
- `SiteSettingRead` includes id, key, updated_at — ✔️  

**Suggestions**
- For structured settings, consider `value: Any` with JSON validation.  

---

## 7. AuditLog Schemas (`app/schemas/audit_log.py`)
**Status:** ✅ Matches model and intended use  
**Highlights**
- `AuditLogBase` with `action`, `resource_type`, `resource_id` — ✔️  
- `AuditLogCreate` adds `user_id` — ✔️  
- `AuditLogRead` includes id, user_id, timestamp — ✔️  

**Suggestions**
- Consider adding optional `details` field (JSON/Text) for richer audit context.  

---

## Summary

| Schema | Completeness | Alignment | Notes |
|--------|--------------|-----------|-------|
| User | ✅ Full | ✅ Matches model | Role validation optional |
| Page | ✅ Full | ✅ Matches model | Slug validation optional |
| PageBlock | ✅ Full | ✅ Matches model | Content JSON validation optional |
| PageRevision | ✅ Full | ✅ Matches model | Status enum optional |
| Media | ✅ Full | ✅ Matches model | filesize optional |
| SiteSetting | ✅ Full | ✅ Matches model | Structured value optional |
| AuditLog | ✅ Full | ✅ Matches model | Optional details field |

---

## Next Steps (Phase 2c → Phase 3 Preparation)
1. **Confirm CRUD layer** (`app/crud/`) implements these schemas correctly.  
2. **Check Pydantic validators** for security-critical fields (passwords, email, slugs).  
3. **Document schema → model mapping** in `backend_audit_phase2_schemas.md`.  
4. Proceed to **Phase 3: API Route & Security Audit** to validate auth, permissions, and endpoint correctness.
