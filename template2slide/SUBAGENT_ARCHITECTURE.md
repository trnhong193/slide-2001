# Kiến Trúc Subagent cho Slide Generation

## Tổng Quan

Bài toán generate slides được chia thành **2 subagents** để đảm bảo chất lượng và tự động hóa quy trình review:

1. **Subagent 1: Generate Slides** - Tạo slides từ template
2. **Subagent 2: Review & Validate** - So sánh slides với template .md, kiểm tra lỗi và lặp lại cho đến khi không còn lỗi

---

## Subagent 1: Generate Slides

### Mục đích
Chuyển đổi template markdown (.md) thành slide structure (JSON) và PowerPoint (.pptx)

### Input
- Template file (.md) - đã được presales approve, không có placeholders
- Output directory (optional)

### Output
- `[Project_Name]_architecture_diagram.md` - Mermaid diagram
- `[Project_Name]_project_info.json` - Project metadata
- `[Project_Name]_slide_structure.json` - Slide structure JSON
- `[Project_Name]_proposal.pptx` - PowerPoint file

### Quy trình
```
Template.md
    ↓
[Step 1] Generate Architecture Diagram
    ↓
[Step 2] Map Content to Slide Structure (JSON)
    ↓
[Step 3] Generate PowerPoint from JSON
    ↓
Output Files (JSON + PPTX)
```

### Scripts sử dụng
- `scripts/template2slide.py` - Main orchestration
- `scripts/generate_from_deal_transfer.py` - Architecture generation
- `scripts/map_to_slides.py` - Content mapping
- `scripts/generate_from_json.js` - PowerPoint generation

### Trách nhiệm
- ✅ Parse template markdown
- ✅ Extract sections và content
- ✅ Generate architecture diagram
- ✅ Map sections to slide structure
- ✅ Create PowerPoint presentation
- ✅ Handle errors trong quá trình generation

---

## Subagent 2: Review & Validate

### Mục đích
So sánh slides đã generate với template .md gốc, phát hiện lỗi và yêu cầu regenerate cho đến khi không còn lỗi

### Input
- Template file gốc (.md)
- Generated slide structure JSON
- Generated PowerPoint file (.pptx) - optional, để check visual

### Output
- Validation report (JSON hoặc markdown)
- List of errors/issues found
- Recommendations for fixes
- **Decision**: PASS (no errors) hoặc FAIL (có errors, cần regenerate)

### Quy trình Validation

```
Generated Slides (JSON + PPTX)
    ↓
[Step 1] Extract content từ template .md
    ↓
[Step 2] Extract content từ slide structure JSON
    ↓
[Step 3] Compare & Validate
    ├─ Content completeness check
    ├─ Field extraction validation
    ├─ Module information validation
    ├─ Architecture diagram validation
    └─ Format consistency check
    ↓
[Step 4] Generate Report
    ├─ List all errors
    ├─ List all warnings
    └─ Provide recommendations
    ↓
[Decision]
    ├─ PASS → Done ✅
    └─ FAIL → Request regenerate (back to Subagent 1)
```

### Validation Rules

#### 1. Content Completeness
- ✅ Tất cả sections trong template phải có trong slides
- ✅ Không được bỏ sót nội dung quan trọng
- ✅ Số lượng slides phù hợp với nội dung

#### 2. Field Extraction Validation
- ✅ Project Requirement Statement: Tất cả fields được extract đúng
- ✅ Module information: Purpose, Alert Logic, Preconditions phải có (không được empty)
- ✅ Timeline milestones: Tất cả phases được extract
- ✅ System Requirements: Tất cả subsections được map

#### 3. Module Information Validation
Cho mỗi module, kiểm tra:
- ✅ Module name extracted
- ✅ Module type extracted (Standard/Custom)
- ✅ Purpose Description: **KHÔNG được empty**
- ✅ Alert Trigger Logic: **KHÔNG được empty**
- ✅ Preconditions: **KHÔNG được empty**
- ⚠️ Image URL: Có thể empty
- ⚠️ Video URL: Có thể empty

#### 4. Architecture Diagram Validation
- ✅ Diagram code exists và valid
- ✅ Matches deployment method từ template
- ✅ Contains all AI modules mentioned

#### 5. Format Consistency
- ✅ Slide numbering continuous
- ✅ Slide types match expected structure
- ✅ Content format consistent

### Error Types

#### Critical Errors (must fix)
- ❌ Missing required sections
- ❌ Empty required fields (Purpose, Alert Logic, Preconditions)
- ❌ Module information incomplete
- ❌ Architecture diagram missing
- ❌ Content mismatch với template

#### Warnings (should fix)
- ⚠️ Optional fields missing (Image URL, Video URL)
- ⚠️ Format inconsistencies
- ⚠️ Content formatting issues

### Iteration Logic

```python
max_iterations = 5  # Prevent infinite loops
iteration = 0

while iteration < max_iterations:
    # Generate slides
    result = subagent1.generate(template_file)
    
    # Review & validate
    validation = subagent2.validate(template_file, result)
    
    if validation.passed:
        break  # Success!
    
    # Log errors
    print(f"Iteration {iteration + 1}: Found {len(validation.errors)} errors")
    for error in validation.errors:
        print(f"  - {error}")
    
    iteration += 1

if iteration >= max_iterations:
    raise Exception("Max iterations reached. Please fix template manually.")
```

---

## Integration Flow

### Main Orchestrator

```python
def generate_slides_with_validation(template_file, output_dir):
    """
    Main function: Generate slides với automatic validation loop
    """
    iteration = 0
    max_iterations = 5
    
    while iteration < max_iterations:
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration + 1}")
        print(f"{'='*80}\n")
        
        # Step 1: Generate slides
        print("📝 Subagent 1: Generating slides...")
        result = subagent1_generate(template_file, output_dir)
        
        # Step 2: Validate
        print("\n🔍 Subagent 2: Validating slides...")
        validation = subagent2_validate(template_file, result)
        
        # Check result
        if validation.passed:
            print("\n✅ Validation PASSED! Slides are ready.")
            return result
        
        # Report errors
        print(f"\n❌ Validation FAILED: {len(validation.errors)} error(s) found")
        for error in validation.errors:
            print(f"   - {error}")
        
        # If critical errors, try to auto-fix or request manual fix
        if validation.has_critical_errors:
            print("\n⚠️  Critical errors detected. Attempting auto-fix...")
            # Auto-fix logic here (if possible)
        
        iteration += 1
    
    # Max iterations reached
    raise Exception(
        f"Failed after {max_iterations} iterations. "
        "Please review template and fix issues manually."
    )
```

---

## Implementation Plan

### Phase 1: Subagent 1 (Generate Slides)
- ✅ Đã có sẵn: `scripts/template2slide.py`
- ✅ Đã có sẵn: `scripts/map_to_slides.py`
- ✅ Đã có sẵn: `scripts/generate_from_json.js`
- **Status**: Hoàn thành, chỉ cần wrap thành subagent function

### Phase 2: Subagent 2 (Review & Validate)
- ⚠️ Cần tạo mới: `scripts/validate_slides.py`
- ⚠️ Cần tạo mới: Validation logic
- ⚠️ Cần tạo mới: Comparison engine
- **Status**: Cần implement

### Phase 3: Integration
- ⚠️ Cần tạo mới: Main orchestrator với loop
- ⚠️ Cần tạo mới: Error reporting
- ⚠️ Cần tạo mới: Auto-fix logic (optional)
- **Status**: Cần implement

---

## File Structure

```
template2slide/
├── scripts/
│   ├── template2slide.py          # Main orchestrator (existing)
│   ├── subagent1_generate.py      # Subagent 1 wrapper (new)
│   ├── subagent2_validate.py      # Subagent 2 (new)
│   ├── validate_slides.py         # Validation logic (new)
│   └── generate_with_validation.py # Main entry point với loop (new)
├── SKILL.md                        # Updated với subagent architecture
└── SUBAGENT_ARCHITECTURE.md       # This file
```

---

## Usage

### Basic Usage (với validation loop)
```bash
python scripts/generate_with_validation.py <template_file.md> [output_dir]
```

### Generate only (Subagent 1)
```bash
python scripts/subagent1_generate.py <template_file.md> [output_dir]
```

### Validate only (Subagent 2)
```bash
python scripts/subagent2_validate.py <template_file.md> <slide_structure.json>
```

---

## Benefits

1. **Quality Assurance**: Tự động phát hiện lỗi trước khi deliver
2. **Iterative Improvement**: Tự động regenerate khi có lỗi
3. **Separation of Concerns**: Generate và Validate tách biệt
4. **Debugging**: Dễ debug khi biết rõ lỗi ở bước nào
5. **Scalability**: Có thể thêm validation rules dễ dàng

---

## Next Steps

1. ✅ Tạo `scripts/subagent2_validate.py` với validation logic
2. ✅ Tạo `scripts/generate_with_validation.py` với iteration loop
3. ✅ Update `SKILL.md` với subagent architecture
4. ✅ Test với real templates
5. ✅ Refine validation rules dựa trên test results



