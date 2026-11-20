# Module 13 — API Design

**Versioning:** `/api/v1` already implemented using APIRouter. URL versioning is easy to discover, test, and document.

**Response standard:**
- Success: `{"success": true, "message": "OK", "data": {}}`
- Error: `{"success": false, "error": {"code": "NOT_FOUND", "message": "Product not found"}}`

**Pagination standard:** `total`, `page`, `limit`, `items`. Existing `skip/limit` pagination can be migrated later.

**Idempotency:** Retrying `POST /products` can create duplicates unless uniqueness or retry protection exists. A future `Idempotency-Key` implementation will store the first successful response and return it for matching retries.

**Example warehouse products:**
- `SCN-001` — Barcode Scanner
- `BOX-002` — Packaging Box
- `LBL-003` — Shipping Label

**Pending:** Apply common response/error envelopes and standardized pagination to every endpoint.