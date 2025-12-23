# Configuration Guide

## 📝 Overview

The test analyzer uses a configuration file (`config.yaml`) to control quality thresholds, report settings, and other behaviors. This allows you to **customize the rules** without modifying code.

---

## 🎯 Quality Status Thresholds

### **Where It's Defined**
File: `config.yaml`

```yaml
quality_thresholds:
  good: 90          # Pass rate >= 90% = GOOD status (Green 🟢)
  acceptable: 75    # Pass rate >= 75% = NEEDS ATTENTION status (Yellow 🟡)
  # Pass rate < 75% = CRITICAL status (Red 🔴)
```

### **How It Works**

The quality status is calculated based on the **pass rate**:

| Pass Rate | Status | Icon | Color | Description |
|-----------|--------|------|-------|-------------|
| ≥ 90% | GOOD | 🟢 | Green | Excellent test quality |
| ≥ 75% | NEEDS ATTENTION | 🟡 | Yellow | Acceptable but watch closely |
| < 75% | CRITICAL | 🔴 | Red | Immediate action required |

### **Your Current Settings**

Based on your test results:
- **Total Tests**: 134
- **Pass Rate**: 67.16%
- **Status**: 🔴 CRITICAL (because 67.16% < 75%)

### **How to Change Thresholds**

Edit `config.yaml` and modify the values:

```yaml
quality_thresholds:
  good: 85          # Lower from 90 to 85
  acceptable: 70    # Lower from 75 to 70
```

With these new settings:
- ≥ 85% = GOOD
- ≥ 70% = NEEDS ATTENTION  
- < 70% = CRITICAL

Your 67.16% pass rate would **still be CRITICAL** with these settings.

---

## ⚙️ Configuration Options

### **1. Quality Thresholds**

Controls when status changes from GOOD → NEEDS ATTENTION → CRITICAL

```yaml
quality_thresholds:
  good: 90          # Minimum pass rate for GOOD status
  acceptable: 75    # Minimum pass rate for NEEDS ATTENTION status
```

**Use Cases:**
- **Strict Environment** (Production): Set to 95/85 for higher standards
- **Development Environment**: Set to 80/60 for more lenient thresholds
- **Legacy Systems**: Set to 70/50 if historically low pass rates

---

### **2. Priority Thresholds**

Controls when to trigger HIGH/MEDIUM priority alerts based on failure counts

```yaml
priority_thresholds:
  # Number of failures to trigger HIGH priority alert
  authentication_high: 5
  authorization_high: 5
  
  # Number of failures to trigger MEDIUM priority alert
  performance_medium: 5
  ui_interaction_medium: 5
  data_validation_medium: 3
```

**Example:**
- If you have 17 authentication failures (like in your data), it triggers HIGH priority because 17 > 5
- If you have 3 UI failures, it triggers MEDIUM priority because 3 ≥ 3

**How to adjust:**
```yaml
priority_thresholds:
  authentication_high: 10    # Raise threshold to 10 failures
  performance_medium: 3      # Lower threshold to 3 failures
```

---

### **3. Report Settings**

Controls what appears in generated reports

```yaml
report_settings:
  # Maximum number of failure categories to show in summary
  max_categories_in_summary: 5
  
  # Maximum number of environments to show in distribution
  max_environments_in_summary: 5
  
  # Include recommendations in reports
  include_recommendations: true
  
  # Include environment distribution in reports
  include_environment_distribution: true
```

**Customization Examples:**

Show more failure categories:
```yaml
max_categories_in_summary: 10
```

Hide environment distribution:
```yaml
include_environment_distribution: false
```

---

### **4. Email Settings** (Future Enhancement)

Placeholder for email automation configuration

```yaml
email_settings:
  subject_prefix: "Test Analysis Summary"
  include_timestamp: true
  # recipients:
  #   - qa-team@company.com
  #   - stakeholders@company.com
```

---

### **5. Notification Settings** (Future Enhancement)

```yaml
notification_settings:
  notify_on_status_change: true
  notify_on_pass_rate_drop: true
  critical_pass_rate_threshold: 75
  notify_on_high_priority: true
  high_priority_failure_count: 10
```

---

## 🔧 Common Configuration Scenarios

### **Scenario 1: Relaxing Thresholds for Development**

```yaml
quality_thresholds:
  good: 80
  acceptable: 60
```

**Result**: Your 67.16% would be "NEEDS ATTENTION" instead of "CRITICAL"

---

### **Scenario 2: Stricter Production Standards**

```yaml
quality_thresholds:
  good: 95
  acceptable: 85
```

**Result**: Even 90% pass rate would be "NEEDS ATTENTION"

---

### **Scenario 3: Reduce Alert Noise**

```yaml
priority_thresholds:
  authentication_high: 20    # Only alert if 20+ failures
  performance_medium: 10     # Only alert if 10+ failures
```

**Result**: Fewer "HIGH PRIORITY" alerts in your reports

---

### **Scenario 4: Focus on Specific Issues**

```yaml
priority_thresholds:
  authentication_high: 1     # Alert on ANY auth failure
  performance_medium: 100    # Ignore perf issues unless severe
```

**Result**: High sensitivity to auth issues, low sensitivity to performance

---

## 📊 How Configuration Affects Your Reports

### **Executive Summary**

The quality status badge color and text are determined by thresholds:

**HTML Report:**
```html
<span style="background-color: #dc3545; color: white;">🔴 CRITICAL</span>
```

**Plain Text Email:**
```
Quality Status: CRITICAL
```

**Markdown:**
```markdown
- **Quality Status**: 🔴 CRITICAL
```

---

### **Priority Recommendations**

Based on your configuration, recommendations are generated:

```
🎯 Priority Recommendations:
  🔴 HIGH PRIORITY: Authentication/Authorization (17 issues)
    → Review user management and access control systems
    
  🟡 MEDIUM PRIORITY: Performance/Connectivity (13 issues)
    → Optimize infrastructure and network configurations
    
  🔴 HIGH PRIORITY: Overall Quality Alert
    → Pass rate (67.2%) is below acceptable threshold (75%)
```

---

## 🔄 Changing Configuration (Step-by-Step)

### **Step 1: Open config.yaml**

```powershell
notepad C:\Automation\LangExtract\config.yaml
```

### **Step 2: Edit Thresholds**

Example - Make thresholds more lenient:
```yaml
quality_thresholds:
  good: 85
  acceptable: 65
```

### **Step 3: Save File**

Save and close the file

### **Step 4: Re-run Analysis**

```powershell
python analyze_tests.py --input "C:\Users\senthil.vivekanandan\Downloads\test results" --enhanced
```

### **Step 5: Verify Changes**

You should see:
```
✅ Loaded configuration from config.yaml
```

And your quality status will be calculated using the new thresholds!

---

## 🎯 Default vs Custom Configuration

### **Default Settings** (if config.yaml is missing)

The analyzer has built-in defaults:
- Good threshold: 90%
- Acceptable threshold: 75%

These are industry-standard thresholds for most test suites.

### **Custom Settings** (when config.yaml exists)

Your custom values override the defaults automatically.

---

## 💡 Best Practices

### **1. Start with Defaults**
Don't change thresholds immediately. Run a few cycles to understand your baseline.

### **2. Adjust Based on Reality**
If you're consistently CRITICAL but tests are actually fine, raise thresholds.

### **3. Match Environment Type**
- **Production**: Strict thresholds (95/85)
- **Staging**: Standard thresholds (90/75)  
- **Development**: Relaxed thresholds (80/65)

### **4. Document Your Changes**
Add comments in config.yaml:
```yaml
quality_thresholds:
  good: 85          # Adjusted for legacy system baseline - 2025-11-13
  acceptable: 70    # Reflects realistic achievable targets
```

### **5. Version Control**
Commit config.yaml to your repository so changes are tracked.

---

## 🚨 Important Notes

### **Changing Thresholds Doesn't Fix Tests**
- Lowering thresholds just changes the status label
- The actual test failures remain
- Use this to set **realistic expectations**, not hide problems

### **Status is a Guide, Not a Goal**
- CRITICAL status with 67% pass rate alerts stakeholders
- It doesn't mean the system is broken, just below threshold
- Investigate the root causes, don't just tweak numbers

### **Consistency Matters**
- Pick thresholds and stick with them
- Changing frequently makes trend analysis difficult
- Document the rationale for any changes

---

## 📈 Example: Your Current Situation

### **Current Configuration**
```yaml
quality_thresholds:
  good: 90
  acceptable: 75
```

### **Your Test Results**
- Pass Rate: 67.16%
- Status: 🔴 CRITICAL

### **Options**

**Option 1: Keep thresholds, fix tests**
- Standard is 75%, you're at 67%
- Focus on fixing the 17 authentication failures
- Goal: Improve pass rate to 75%+

**Option 2: Adjust thresholds temporarily**
```yaml
quality_thresholds:
  good: 85
  acceptable: 65
```
- Your 67% would be "NEEDS ATTENTION" (yellow)
- Less alarming to stakeholders
- Set improvement goal to reach 85%

**Option 3: Dual thresholds**
- Use strict thresholds (90/75) for production
- Use relaxed thresholds (80/60) for development
- Maintain two config files and switch based on environment

---

## 🎓 Summary

| Setting | Default | What It Controls | Where Used |
|---------|---------|------------------|------------|
| `good` | 90 | GOOD status threshold | All reports |
| `acceptable` | 75 | NEEDS ATTENTION threshold | All reports |
| `max_categories_in_summary` | 5 | Number of categories shown | Executive summaries |
| `authentication_high` | 5 | HIGH priority threshold | Recommendations |

**Configuration File**: `config.yaml`  
**How to Change**: Edit file, save, re-run analyzer  
**Recommendation**: Start with defaults, adjust based on your reality

---

**Last Updated**: November 13, 2025  
**Your Configuration**: Using `config.yaml` with thresholds 90/75