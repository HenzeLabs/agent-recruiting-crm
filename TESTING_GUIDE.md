# AutoMentor CRM - Testing Guide

## Overview

Comprehensive test suite validating all CRM functionality across realistic recruiting workflows.

## Test Structure

### 📝 Level 1: Intake - Data Entry

**Script:** `add_demo_data.py`  
**Purpose:** Generate realistic test data with various completeness levels

**Scenarios:**

- ✅ 15 complete records (all fields)
- ✅ 10 partial records (missing phone or email)
- ✅ 5 minimal records (name only)
- ✅ 8 stale records (>3 days old, needing follow-up)
- ✅ 3 duplicate emails
- ✅ 5 edge cases (invalid formats, special characters, long names)
- ✅ Additional records to reach 100+ total

**Usage:**

```bash
python add_demo_data.py
```

---

### 🧪 Level 2: API Unit Tests

**Script:** `tests/test_api.py` (pytest)  
**Purpose:** Test all API endpoints and CRUD operations

**Test Classes:**

1. **TestRecruitsCRUD** - Basic CRUD operations

   - Create (complete, partial, minimal)
   - Read (all, by ID, not found)
   - Update (fields, stages)
   - Delete (single, not found)

2. **TestStageTransitions** - Workflow validation

   - Forward progression (New → Licensed)
   - Backward transitions (Licensed → Contacted)
   - Inactive stage handling

3. **TestEdgeCases** - Error handling

   - Duplicate emails
   - Special characters
   - Very long names
   - Invalid JSON
   - Empty bodies

4. **TestBulkOperations** - Performance validation

   - Create 20+ records
   - Update 20+ records
   - Delete 20+ records

5. **TestDataPersistence** - Data integrity

   - Timestamps on create
   - Timestamps on update

6. **TestValidation** - Input validation
   - Required field enforcement
   - Format validation (currently minimal)

**Usage:**

```bash
pytest tests/test_api.py -v
```

**Expected Output:**

```
tests/test_api.py::TestRecruitsCRUD::test_create_recruit_complete PASSED
tests/test_api.py::TestRecruitsCRUD::test_create_recruit_minimal PASSED
tests/test_api.py::TestRecruitsCRUD::test_create_recruit_no_name PASSED
...
====== 40 passed in 2.34s ======
```

---

### 🎭 Level 3: End-to-End Tests

**Script:** `tests/crm.spec.js` (Playwright)  
**Purpose:** Test complete user workflows through browser

**Test Suites:**

1. **Level 1: Intake - Data Entry**

   - Add complete recruit (all fields)
   - Add partial recruit (missing phone)
   - Add minimal recruit (name only)
   - Form validation (name required)
   - Dashboard instant refresh

2. **Level 2: Stage Transitions**

   - Single stage update
   - Bulk stage updates (3+ recruits)
   - Keyboard navigation in dropdown

3. **Level 3: Edit & Delete Flow**

   - Edit without page refresh
   - Delete and update counts
   - Delete one per stage

4. **Level 4: Dashboard Integrity**

   - All stage cards displayed
   - Cards render correctly (10+ entries)
   - Smooth scroll performance

5. **Level 5: Persistence & Refresh**

   - Data persists across refresh
   - Timestamps preserved after edits

6. **Level 6: Edge Cases**

   - Duplicate emails handled
   - Very long names display correctly
   - Special characters sanitized
   - Backward stage transitions

7. **Level 7: Mobile Responsiveness**
   - Mobile viewport (375px)
   - Tablet viewport (768px)

**Usage:**

```bash
npx playwright test
```

**Expected Output:**

```
Running 25 tests using 1 worker

  ✓ Level 1: Intake - should add complete recruit
  ✓ Level 1: Intake - should add partial recruit
  ✓ Level 2: Stage Transitions - should update stage
  ...

25 passed (45.2s)
```

---

### 💪 Level 4: Load & Performance Tests

**Script:** `tests/load_test.py`  
**Purpose:** Validate performance under realistic load

**Test Scenarios:**

1. **API Response Times** (3 iterations)

   - Target: < 200ms average
   - Measures: GET /api/recruits

2. **Dashboard Load Times** (3 iterations)

   - Target: < 1000ms average
   - Measures: GET / (full HTML render)

3. **Bulk Creates** (20 records)

   - Target: < 100ms per operation
   - Measures: POST /api/recruits throughput

4. **Bulk Updates** (20 records)

   - Target: < 100ms per operation
   - Measures: PUT /api/recruits/:id

5. **Bulk Deletes** (20 records)

   - Target: < 100ms per operation
   - Measures: DELETE /api/recruits/:id

6. **Large Dataset Performance** (100+ records)

   - Target: Dashboard load < 1000ms
   - Validates: Scroll smoothness, rendering

7. **Concurrent Reads** (5 simultaneous × 10 iterations)
   - Target: < 500ms average
   - Validates: Database concurrency handling

**Usage:**

```bash
python tests/load_test.py
```

**Expected Output:**

```
══════════════════════════════════════════════════════════════════
AUTOMENTOR CRM - LOAD TESTING SUITE
══════════════════════════════════════════════════════════════════

▸ Checking server availability...
✓ Server is running

▸ Testing API response times (3 iterations)...
✓ API response times measured
  Average................................... 45.23 ms
  Min....................................... 42.11 ms
  Max....................................... 49.87 ms

▸ Testing dashboard load times (3 iterations)...
✓ Dashboard load times measured
  Average................................... 234.56 ms
  ...

✅ All performance targets met
```

---

## Running All Tests

### Quick Run (All Tests)

```bash
./run_tests.sh
```

This script:

1. ✅ Checks dependencies (pip, npm, playwright)
2. ✅ Starts Flask server if not running
3. ✅ Generates demo data (100+ records)
4. ✅ Runs pytest API tests
5. ✅ Runs Playwright E2E tests
6. ✅ Runs load/performance tests
7. ✅ Generates TEST_RESULTS.md report

### Individual Test Runs

**API Tests Only:**

```bash
source venv/bin/activate
pytest tests/test_api.py -v
```

**E2E Tests Only:**

```bash
npx playwright test --headed  # Watch browser
npx playwright test --debug   # Step through
```

**Load Tests Only:**

```bash
source venv/bin/activate
python tests/load_test.py
```

**Generate Demo Data Only:**

```bash
source venv/bin/activate
python add_demo_data.py
```

---

## Test Results

After running `./run_tests.sh`, review:

1. **TEST_RESULTS.md** - Comprehensive pass/fail matrix
2. **test_output_api.log** - Detailed pytest output
3. **test_output_playwright.log** - E2E test details
4. **test_output_load.log** - Performance metrics

---

## Pass/Fail Criteria

### ✅ System Passes If:

- All API CRUD operations work correctly
- Form validation enforces required fields
- Dashboard updates without page refresh
- Stage transitions (forward/backward) succeed
- Data persists across page refreshes
- Handles 100+ records smoothly
- Response times < target thresholds
- Mobile viewports render correctly

### ❌ System Fails If:

- Data loss occurs
- Database errors on valid input
- Dashboard doesn't update after operations
- Performance exceeds thresholds (200ms API, 1s dashboard)
- Layout breaks on mobile
- XSS vulnerabilities exist

---

## Debugging Failed Tests

### API Tests Fail

```bash
# Check database
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM recruits;"

# Verify server running
curl http://127.0.0.1:5000/api/recruits

# Run single test with verbose output
pytest tests/test_api.py::TestRecruitsCRUD::test_create_recruit_complete -vv
```

### E2E Tests Fail

```bash
# Run in headed mode to see browser
npx playwright test --headed

# Debug mode (step through)
npx playwright test --debug

# Screenshot on failure (automatic)
# Check: test-results/screenshots/
```

### Load Tests Fail

```bash
# Check server performance manually
curl -w "@curl-format.txt" http://127.0.0.1:5000/api/recruits

# Reduce load test iterations
# Edit tests/load_test.py: TEST_ITERATIONS = 1
```

---

## Test Data Cleanup

**Clear all test data:**

```bash
# Backup first
cp db.sqlite3 db.sqlite3.backup

# Clear recruits table
sqlite3 db.sqlite3 "DELETE FROM recruits;"

# Or start fresh
rm db.sqlite3
python app.py  # Reinitializes empty DB
```

**Restore backup:**

```bash
mv db.sqlite3.backup db.sqlite3
```

---

## Performance Benchmarks

### Expected Performance (on modern hardware)

| Operation                    | Target   | Typical |
| ---------------------------- | -------- | ------- |
| API GET (empty)              | < 50ms   | ~25ms   |
| API GET (100 records)        | < 200ms  | ~75ms   |
| Dashboard load (100 records) | < 1000ms | ~300ms  |
| CREATE operation             | < 100ms  | ~35ms   |
| UPDATE operation             | < 100ms  | ~40ms   |
| DELETE operation             | < 100ms  | ~30ms   |

### If Performance Degrades:

- Check database size (SQLite indexes)
- Monitor server resources (CPU/memory)
- Test on production-like environment
- Consider database optimization (VACUUM)

---

## Continuous Integration

### GitHub Actions (example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: npx playwright install chromium
      - run: ./run_tests.sh
```

---

## Manual Testing Checklist

Beyond automated tests, manually verify:

- [ ] Add recruit via form submits correctly
- [ ] Edit recruit shows pre-filled values
- [ ] Delete recruit shows confirmation
- [ ] Stage dropdown colors match semantic meaning
- [ ] Mobile navigation stacks vertically
- [ ] Touch targets are 44px minimum
- [ ] Cards have smooth hover effects
- [ ] Glassmorphism blur renders correctly
- [ ] Browser back button works
- [ ] Keyboard tab order is logical
- [ ] Screen reader announces form labels

---

## Questions?

**Test not running?**

- Ensure server is running: `python app.py`
- Check port 5000 is free: `lsof -ti:5000`
- Verify dependencies: `pip install -r requirements.txt`

**Need more test coverage?**

- Add tests to `tests/test_api.py` for new endpoints
- Add E2E scenarios to `tests/crm.spec.js`
- Extend load tests in `tests/load_test.py`

**Performance concerns?**

- Run load tests with different record counts
- Profile with: `python -m cProfile app.py`
- Check SQLite query plans: `EXPLAIN QUERY PLAN ...`
