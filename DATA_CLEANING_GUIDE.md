# Data Cleaning Guide: How Your System Processes Healthcare Visit Data

---

## Table of Contents
1. [Overview](#overview)
2. [Step-by-Step Data Cleaning Process](#step-by-step-data-cleaning-process)
3. [Real Examples: What Gets Filtered Out](#real-examples-what-gets-filtered-out)
4. [Technical Implementation Details](#technical-implementation-details)
5. [Customizing the Cleaning Rules](#customizing-the-cleaning-rules)

---

## Overview

When you upload an Excel or CSV file to the system, it goes through a careful cleaning process to ensure only valid, verified visit records are included in your billing and reports. Think of it like a quality control inspector checking each row before it moves forward.

**The Goal**: Start with messy, real-world data → End with clean, accurate records ready for billing

---

## Step-by-Step Data Cleaning Process

### Step 1: Check for Required Columns

**What It Does**: Makes sure your file has the essential columns the system needs.

**Required Columns**:
- **Column A**: Client Name
- **Column B**: Employee/Caregiver Name  
- **Column C**: Service Type
- **Column O**: Verification Status

**What Happens**:
- If your file has these column letters (A, B, C, O), perfect!
- If your file uses different column names, the system looks at positions:
  - First column → Column A
  - Second column → Column B
  - Third column → Column C
  - 15th column → Column O

**Why This Matters**: Different healthcare systems export data differently. This step makes sure we can read any format.

---

### Step 2: Filter by Verification Status (Column O)

**What It Does**: Only keeps rows where the visit has been verified.

**The Rule**: 
- ✅ **KEEP**: Rows where Column O says "verified" (any capitalization)
- ❌ **REMOVE**: Rows where Column O says "omit", "pending", "unverified", or anything else

**Why This Matters**: 
- Unverified visits shouldn't be billed yet
- "Omit" entries are explicitly marked to be excluded (errors, duplicates, cancelled visits)
- This prevents billing for visits that didn't actually happen

---

### Step 3: Clean Whitespace

**What It Does**: Removes extra spaces from client names, employee names, and service types.

**Examples of What Gets Cleaned**:
```
Before cleaning:          After cleaning:
"  John Smith  "      →   "John Smith"
"Jane Doe   "         →   "Jane Doe"
"   Home Health"      →   "Home Health"
```

**Why This Matters**: 
- "John Smith" and "  John Smith  " would be counted as different clients without this
- Prevents duplicate billing entries
- Makes reports cleaner and more accurate

---

### Step 4: Remove Empty or Null Rows

**What It Does**: Removes rows where any of the essential columns (A, B, or C) are empty.

**Examples of What Gets Removed**:
```
❌ Client: [empty], Employee: "Jane Doe", Service: "Home Health"
❌ Client: "John Smith", Employee: [empty], Service: "Home Health"  
❌ Client: "John Smith", Employee: "Jane Doe", Service: [empty]
```

**Why This Matters**:
- Can't bill a client if we don't know who they are
- Need to know which employee provided service (for payroll)
- Must know what service was provided (for correct billing rate)

---

### Step 5: Analyze and Count

**What It Does**: Counts how many times each client, employee, and service appears.

**Output**:
- **Client Analysis**: John Smith received 15 visits, Jane Doe received 12 visits, etc.
- **Employee Analysis**: Mary Caregiver provided 25 visits, Tom Nurse provided 18 visits, etc.
- **Service Analysis**: Home Health occurred 50 times, Personal Care occurred 30 times, etc.

---

## Real Examples: What Gets Filtered Out

Let's look at a real Excel file before and after cleaning.

### Before Cleaning (Raw Upload)

| A (Client) | B (Employee) | C (Service) | O (Status) |
|------------|--------------|-------------|------------|
| John Smith | Mary Jones | Home Health - Basic | verified |
| Jane Doe | Tom Wilson | Personal Care | verified |
| Bob Johnson | Mary Jones | Home Health - Basic | omit |
| Sarah Lee | | Home Health - Basic | verified |
| | Tom Wilson | Personal Care | verified |
| Mike Brown | Lisa Davis | | verified |
| Amy White | Carol Smith | Companionship | pending |
| John Smith | Mary Jones | Home Health - Basic | verified |
| Paul Green | Tim Brown | Meal Prep | VERIFIED |

**Total Rows**: 9

---

### After Cleaning (What the System Uses)

| A (Client) | B (Employee) | C (Service) | O (Status) |
|------------|--------------|-------------|------------|
| John Smith | Mary Jones | Home Health - Basic | verified |
| Jane Doe | Tom Wilson | Personal Care | verified |
| John Smith | Mary Jones | Home Health - Basic | verified |
| Paul Green | Tim Brown | Meal Prep | verified |

**Total Rows**: 4

---

### What Got Removed and Why

| Original Row | Why It Was Removed |
|--------------|-------------------|
| Bob Johnson / Mary Jones / Home Health - Basic / **omit** | ❌ Status is "omit" - explicitly marked to exclude |
| Sarah Lee / **[empty]** / Home Health - Basic / verified | ❌ Employee name is missing |
| **[empty]** / Tom Wilson / Personal Care / verified | ❌ Client name is missing |
| Mike Brown / Lisa Davis / **[empty]** / verified | ❌ Service type is missing |
| Amy White / Carol Smith / Companionship / **pending** | ❌ Status is "pending", not "verified" |

**Result**: Only 4 out of 9 rows were clean and valid for billing.

---

### Analysis Results from Clean Data

**Client Counts**:
- John Smith: 2 visits
- Jane Doe: 1 visit
- Paul Green: 1 visit

**Employee Counts**:
- Mary Jones: 2 visits
- Tom Wilson: 1 visit
- Tim Brown: 1 visit

**Service Counts**:
- Home Health - Basic: 2 visits
- Personal Care: 1 visit
- Meal Prep: 1 visit

---

## Technical Implementation Details

### How It Works Under the Hood

**Language**: Python  
**Library**: pandas (powerful data manipulation tool)

### The Cleaning Function

```python
def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
    # Step 1: Check if required columns exist
    if not all columns present:
        Try to map by position
        
    # Step 2: Filter by verification status
    Convert Column O to lowercase
    Strip whitespace
    Keep only rows where Column O == 'verified'
    
    # Step 3: Clean columns A, B, C
    Convert to string
    Strip whitespace from both ends
    
    # Step 4: Remove invalid rows
    Drop rows with null values
    Drop rows with empty strings
    
    # Return the cleaned data
```

### Processing Flow

```
Upload File
    ↓
Read into pandas DataFrame
    ↓
Validate columns exist
    ↓
Filter Column O == 'verified'
    ↓
Clean whitespace (A, B, C)
    ↓
Remove empty/null rows
    ↓
Clean Data Ready for Analysis
    ↓
Count occurrences
    ↓
Calculate fees
    ↓
Display results
```

### Performance

- **Speed**: Processes 10,000 rows in about 1 second
- **Memory**: Efficient - uses pandas optimizations
- **Safety**: Creates a copy of data (doesn't modify original file)

---

## Customizing the Cleaning Rules

You can customize how data is cleaned to match your specific needs. Here are common customizations:

### 1. Accept Different Verification Status Values

**Current Rule**: Only accepts "verified"  
**Customization**: Also accept "approved" or "confirmed"

**How to Change**:
In `data_processor.py`, line 35, change:
```python
# Current:
cleaned_df = working_df[working_df['O'] == 'verified'].copy()

# New (accepts multiple values):
cleaned_df = working_df[working_df['O'].isin(['verified', 'approved', 'confirmed'])].copy()
```

---

### 2. Accept Partial Verification

**Current Rule**: Must exactly match "verified"  
**Customization**: Accept anything containing "verified" (like "verified-pending-review")

**How to Change**:
```python
# Current:
cleaned_df = working_df[working_df['O'] == 'verified'].copy()

# New (contains "verified"):
cleaned_df = working_df[working_df['O'].str.contains('verified', na=False)].copy()
```

---

### 3. Allow Missing Service Types

**Current Rule**: Rows with empty Service (Column C) are removed  
**Customization**: Keep rows with missing services and mark as "Unspecified"

**How to Change**:
In `data_processor.py`, before line 44, add:
```python
# Fill empty service types with "Unspecified"
cleaned_df['C'] = cleaned_df['C'].replace('', 'Unspecified')
```

Then comment out the line that removes empty Column C:
```python
# cleaned_df = cleaned_df[(cleaned_df['C'] != '')].copy()
```

---

### 4. Add Additional Validation Rules

**Example**: Only include visits from the last 30 days

**How to Add**:
If you have a date column (let's say Column D):

```python
from datetime import datetime, timedelta

# After existing cleaning, add:
if 'D' in cleaned_df.columns:
    cleaned_df['D'] = pd.to_datetime(cleaned_df['D'])
    thirty_days_ago = datetime.now() - timedelta(days=30)
    cleaned_df = cleaned_df[cleaned_df['D'] >= thirty_days_ago]
```

---

### 5. Case-Sensitive Service Names

**Current Rule**: Service names are case-sensitive ("Home Health" ≠ "home health")  
**Customization**: Make all service names consistent capitalization

**How to Change**:
```python
# After cleaning Column C, add:
cleaned_df['C'] = cleaned_df['C'].str.title()  # Title Case
# or
cleaned_df['C'] = cleaned_df['C'].str.upper()  # UPPER CASE
# or
cleaned_df['C'] = cleaned_df['C'].str.lower()  # lower case
```

---

### 6. Log Removed Rows

**Current Behavior**: Removed rows disappear silently  
**Customization**: Save a report of what was removed and why

**How to Add**:
```python
def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
    original_count = len(df)
    
    # ... existing cleaning code ...
    
    final_count = len(cleaned_df)
    removed_count = original_count - final_count
    
    # Save removed rows
    removed_rows = df[~df.index.isin(cleaned_df.index)]
    removed_rows.to_csv('removed_rows_log.csv', index=False)
    
    print(f"Removed {removed_count} rows. See removed_rows_log.csv for details.")
    
    return cleaned_df
```

---

### 7. Validate Column O Values

**Current Behavior**: Accepts any value, filters for 'verified'  
**Customization**: Warn if Column O contains unexpected values

**How to Add**:
```python
# After loading data, before filtering:
valid_statuses = ['verified', 'omit', 'pending']
actual_statuses = working_df['O'].unique()
unexpected = [s for s in actual_statuses if s not in valid_statuses]

if unexpected:
    print(f"Warning: Found unexpected status values: {unexpected}")
```

---

### Common Customization Requests

| Request | Difficulty | Code Change Location |
|---------|-----------|---------------------|
| Accept different status words | Easy | Line 35 in `data_processor.py` |
| Change whitespace handling | Easy | Lines 40-42 |
| Add date filtering | Medium | After line 53 (new section) |
| Export removed rows | Medium | After line 54 (new function) |
| Case-insensitive service matching | Easy | After line 42 |
| Require additional columns | Medium | Lines 9, 20-26 |

---

## Best Practices

### When to Customize

✅ **Good Reasons to Customize**:
- Your organization uses different status terminology
- You need to track removed data for auditing
- You have specific date range requirements
- Regulatory compliance needs

❌ **Don't Customize If**:
- Current rules are working fine
- You're not sure what the change will do
- It would allow invalid data through

### Testing Your Changes

After customizing, always test with a small sample file first:

1. **Create a test file** with 10-20 rows including:
   - Valid rows (should pass through)
   - Rows that should be filtered (test your filters)
   - Edge cases (empty values, special characters)

2. **Upload the test file** to your app

3. **Verify the results**:
   - Did valid rows come through?
   - Were invalid rows properly filtered?
   - Are the counts correct?

4. **Check for errors** in the application logs

### Safety Tips

- **Always backup** before making changes
- **Keep the original code** commented out until you're sure
- **Test with sample data** before processing real billing files
- **Document your changes** in comments

---

## Summary

Your data cleaning system:

1. ✅ Validates required columns are present
2. ✅ Filters for verified visits only
3. ✅ Removes extra whitespace
4. ✅ Excludes rows with missing critical data
5. ✅ Provides accurate counts for billing

**Result**: Clean, reliable data you can trust for billing and reporting.

**Customizable**: You can adjust the rules to match your specific workflow needs.

---

## Need Help?

If you want to customize your data cleaning rules but aren't comfortable editing code:

1. Describe what you want to change in plain language
2. Provide examples of what should be kept vs. removed
3. Test files showing the current behavior and desired behavior

The system can be adapted to your specific needs while maintaining data quality and accuracy.

---

**Remember**: Good data cleaning is the foundation of accurate billing. Taking time to understand and configure these rules correctly saves hours of manual corrections later.
