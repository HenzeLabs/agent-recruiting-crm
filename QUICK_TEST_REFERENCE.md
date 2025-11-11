# AutoMentor CRM - Quick Test Reference

## 🚀 Quick Start

```bash
# 1. Generate test data (100+ records)
python add_demo_data.py

# 2. Run all tests
./run_tests.sh

# 3. View results
cat TEST_RESULTS.md
```

---

## 📋 Test Suite Overview

| Level          | Script               | Purpose                | Records     | Duration |
| -------------- | -------------------- | ---------------------- | ----------- | -------- |
| **Intake**     | `add_demo_data.py`   | Generate test data     | 100+        | ~5s      |
| **API Tests**  | `tests/test_api.py`  | Unit test endpoints    | 40+ tests   | ~3s      |
| **E2E Tests**  | `tests/crm.spec.js`  | Browser workflows      | 25+ tests   | ~45s     |
| **Load Tests** | `tests/load_test.py` | Performance validation | 7 scenarios | ~15s     |

**Total Test Time:** ~70 seconds  
**Total Test Coverage:** 70+ automated tests

---

## 🎯 What Gets Tested

### ✅ Data Entry (Intake Level)

- Complete records (all fields)
- Partial records (missing email/phone)
- Minimal records (name only)
- Validation (required name field)
- Instant dashboard refresh

### ✅ Stage Transitions

- Forward: New → Contacted → Training → Licensed
- Backward: Licensed → Contacted (unusual but valid)
- To Inactive: Any stage → Inactive
- Bulk updates: 3+ records simultaneously

### ✅ Follow-Up Logic

- Stale detection: >3 days no contact
- Overdue flagging in dashboard
- Last contact timestamp tracking

### ✅ Edit & Delete

- Inline editing without page refresh
- Immediate dashboard metric updates
- Delete per stage validation
- Soft failure handling

### ✅ Dashboard Integrity

- All 5 stage cards render
- Counts accurate after operations
- Smooth scroll with 100+ records
- Card layout responsive

### ✅ Persistence

- Data survives page refresh
- Timestamps preserved
- Stage positions maintained

### ✅ Edge Cases

- Duplicate emails allowed
- Special characters (@#$%) handled
- Very long names (500+ chars)
- Invalid formats accepted (no strict validation)
- Backward stage transitions work

### ✅ Mobile Responsiveness

- Phone viewport (375px)
- Tablet viewport (768px)
- Touch targets (44px minimum)
- Vertical stacking

### ✅ Performance

- API: < 200ms response
- Dashboard: < 1000ms load
- CRUD: < 100ms per operation
- Concurrent: 5+ simultaneous reads

---

## 📊 Pass/Fail Matrix (Quick Reference)

| Category            | Tests | Expected Result                           |
| ------------------- | ----- | ----------------------------------------- |
| **API CRUD**        | 12    | All pass - create/read/update/delete work |
| **Stage Workflow**  | 3     | All pass - transitions validated          |
| **Validation**      | 4     | All pass - required fields enforced       |
| **Edge Cases**      | 6     | All pass - handles unusual input          |
| **Bulk Ops**        | 3     | All pass - 20+ records handled            |
| **E2E Intake**      | 5     | All pass - form submission works          |
| **E2E Stages**      | 3     | All pass - dropdown updates correctly     |
| **E2E Edit/Delete** | 3     | All pass - AJAX operations smooth         |
| **E2E Persistence** | 2     | All pass - data survives refresh          |
| **E2E Mobile**      | 2     | All pass - responsive layouts work        |
| **Load API**        | 1     | Pass if < 200ms                           |
| **Load Dashboard**  | 1     | Pass if < 1000ms                          |
| **Load CRUD**       | 3     | Pass if < 100ms each                      |
| **Load Dataset**    | 1     | Pass - handles 100+ records               |
| **Load Concurrent** | 1     | Pass if < 500ms                           |

**Total:** ~70 tests across 4 levels

---

## 🔧 Individual Test Commands

### Generate Demo Data

```bash
source venv/bin/activate
python add_demo_data.py
# Select 'y' to clear existing data
```

**Output:**

```
🎭 Adding comprehensive demo data...
📝 LEVEL 1: INTAKE - DATA ENTRY
✓ Added 15 complete records
✓ Added 10 partial records
...
📊 SUMMARY
Total Recruits: 102
```

### Run API Tests

```bash
source venv/bin/activate
pytest tests/test_api.py -v
```

**Output:**

```
tests/test_api.py::TestRecruitsCRUD::test_create_recruit_complete PASSED [10%]
tests/test_api.py::TestRecruitsCRUD::test_get_all_recruits PASSED [20%]
...
====== 40 passed in 2.54s ======
```

### Run E2E Tests

```bash
npx playwright test
```

**Output:**

```
Running 25 tests using 1 worker
✓ Level 1: Intake - should add complete recruit (2.3s)
✓ Level 2: Stage Transitions - should update stage (1.8s)
...
25 passed (42.7s)
```

### Run Load Tests

```bash
source venv/bin/activate
python tests/load_test.py
```

**Output:**

```
══════════════════════════════════════════════════════════════════
AUTOMENTOR CRM - LOAD TESTING SUITE
══════════════════════════════════════════════════════════════════
✓ Server is running
▸ Testing API response times (3 iterations)...
  Average................................... 52.34 ms ✓
...
✓ All performance targets met
```

---

## 🎨 Test Data Breakdown

Demo data script creates:

| Type       | Count | Description                                            |
| ---------- | ----- | ------------------------------------------------------ |
| Complete   | 15    | All fields populated                                   |
| Partial    | 10    | Missing email or phone                                 |
| Minimal    | 5     | Name only                                              |
| Per Stage  | 30    | 8 New, 7 Contacted, 5 Training, 6 Licensed, 4 Inactive |
| Overdue    | 8     | >3 days no contact                                     |
| Duplicates | 3     | Same email address                                     |
| Edge Cases | 5     | Invalid formats, long names, special chars             |
| Bulk       | 40+   | Additional to reach 100+                               |

**Total: 100+ test records**

---

## 📈 Performance Targets

| Metric           | Target   | Excellent | Acceptable | Poor     |
| ---------------- | -------- | --------- | ---------- | -------- |
| API Response     | < 200ms  | < 50ms    | 50-200ms   | > 200ms  |
| Dashboard Load   | < 1000ms | < 300ms   | 300-1000ms | > 1000ms |
| CRUD Operations  | < 100ms  | < 30ms    | 30-100ms   | > 100ms  |
| Concurrent Reads | < 500ms  | < 200ms   | 200-500ms  | > 500ms  |

---

## ✅ Success Criteria

Tests PASS if:

- ✅ All 40+ API tests pass
- ✅ All 25+ E2E tests pass
- ✅ All performance metrics under targets
- ✅ No data loss or corruption
- ✅ Dashboard updates without refresh
- ✅ Mobile viewports render correctly

System is **PRODUCTION READY** if all tests pass.

---

## 🚨 Common Issues

### "Server not running"

```bash
# Start server in separate terminal
python app.py
# Or: ./run_tests.sh will auto-start
```

### "Playwright not installed"

```bash
npm install
npx playwright install chromium
```

### "pytest not found"

```bash
pip install pytest requests
```

### "Database locked"

```bash
# Close any SQLite connections
pkill -f "python app.py"
lsof -ti:5000 | xargs kill -9
```

### "Tests fail on mobile"

```bash
# Check viewport meta tag exists in base.html
grep viewport templates/base.html
```

---

## 📁 Generated Files

After test run:

- `TEST_RESULTS.md` - Comprehensive report with pass/fail matrix
- `test_output_api.log` - Detailed pytest output
- `test_output_playwright.log` - E2E test details
- `test_output_load.log` - Performance metrics
- `db.sqlite3.backup` - Database backup before tests

---

## 🎯 Next Steps After Tests Pass

1. **Deploy to Production**

   ```bash
   git add .
   git commit -m "Add comprehensive test suite"
   git push origin main
   # Deploy to Render/Heroku
   ```

2. **Add CI/CD**

   - GitHub Actions workflow
   - Automated testing on PR
   - Deploy on merge to main

3. **Monitor Performance**

   - Set up error tracking (Sentry)
   - Add analytics (Plausible/Google Analytics)
   - Monitor response times

4. **Enhance Features**
   - Email validation
   - Duplicate detection
   - CSV export
   - Follow-up reminders

---

## 📞 Need Help?

- Review `TESTING_GUIDE.md` for detailed documentation
- Check test logs: `test_output_*.log`
- Run tests in debug mode: `npx playwright test --debug`
- Verify server: `curl http://127.0.0.1:5000/api/recruits`

---

**Last Updated:** $(date)  
**Test Suite Version:** 1.0  
**Coverage:** 70+ automated tests across 4 levels
