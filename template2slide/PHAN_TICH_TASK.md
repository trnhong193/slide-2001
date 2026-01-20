# Phân Tích Task: Generate Slides với Subagent Architecture

## Bài Toán Hiện Tại

Hiện tại, quy trình generate slides từ template .md có thể gặp lỗi:
- ❌ Thiếu thông tin module (Purpose, Alert Logic, Preconditions empty)
- ❌ Content không match với template
- ❌ Format không đúng
- ❌ Phải check thủ công sau khi generate

## Giải Pháp: Chia thành 2 Subagents

Theo gợi ý của sếp, chia task thành 2 subagents:

### Subagent 1: Generate Slides
**Nhiệm vụ**: Tạo slides từ template .md

**Input**: 
- Template file (.md)

**Output**:
- Slide structure JSON
- PowerPoint file (.pptx)

**Quy trình**:
```
Template.md → Architecture → Slide Structure → PowerPoint
```

### Subagent 2: Review & Validate
**Nhiệm vụ**: So sánh slides với template .md, check lỗi

**Input**:
- Template file gốc (.md)
- Generated slides (JSON + PPTX)

**Output**:
- Validation report
- List errors
- Decision: PASS hoặc FAIL

**Quy trình**:
```
Generated Slides + Template.md → Compare → Validation Report
```

## Workflow Tổng Thể

```
┌─────────────────────────────────────────────────────────┐
│  Main Orchestrator                                       │
│                                                          │
│  ┌──────────────────┐                                   │
│  │  Subagent 1      │                                   │
│  │  Generate Slides │                                   │
│  └────────┬─────────┘                                   │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────┐                                   │
│  │  Subagent 2      │                                   │
│  │  Validate        │                                   │
│  └────────┬─────────┘                                   │
│           │                                              │
│           ▼                                              │
│     ┌─────────┐                                         │
│     │  PASS?  │                                         │
│     └────┬────┘                                         │
│          │                                               │
│     ┌────┴────┐                                         │
│     │         │                                          │
│    YES       NO ──────┐                                 │
│     │         │        │                                 │
│     ▼         │        │                                 │
│   ✅ Done     │        │                                 │
│               │        │                                 │
│               ▼        │                                 │
│         Report Errors  │                                 │
│               │        │                                 │
│               └────────┘ (loop back)                    │
└─────────────────────────────────────────────────────────┘
```

## Chi Tiết Validation Rules

### 1. Content Completeness
- ✅ Tất cả sections trong template có trong slides
- ✅ Không bỏ sót nội dung

### 2. Module Information
Cho mỗi module:
- ✅ Module name: Có
- ✅ Module type: Có (Standard/Custom)
- ✅ Purpose: **KHÔNG được empty** ❌
- ✅ Alert Logic: **KHÔNG được empty** ❌
- ✅ Preconditions: **KHÔNG được empty** ❌
- ⚠️ Image URL: Có thể empty
- ⚠️ Video URL: Có thể empty

### 3. Field Extraction
- ✅ Project Requirement: Tất cả fields extracted
- ✅ Timeline: Tất cả phases extracted
- ✅ System Requirements: Tất cả subsections mapped

### 4. Architecture
- ✅ Diagram exists
- ✅ Matches deployment method

## Implementation Plan

### Bước 1: Tạo Subagent 2 (Validation)
File: `scripts/subagent2_validate.py`

Chức năng:
- Parse template .md
- Parse slide structure JSON
- Compare và validate
- Generate report

### Bước 2: Tạo Main Orchestrator
File: `scripts/generate_with_validation.py`

Chức năng:
- Loop: Generate → Validate → Check
- Nếu FAIL: Report errors và regenerate
- Nếu PASS: Done

### Bước 3: Test
- Test với templates có lỗi
- Test với templates đúng
- Verify iteration loop hoạt động

## Lợi Ích

1. ✅ **Tự động phát hiện lỗi**: Không cần check thủ công
2. ✅ **Tự động sửa**: Loop lại cho đến khi hết lỗi
3. ✅ **Tách biệt trách nhiệm**: Generate và Validate riêng biệt
4. ✅ **Dễ debug**: Biết rõ lỗi ở đâu
5. ✅ **Có thể mở rộng**: Thêm validation rules dễ dàng

## Ví Dụ Sử Dụng

```bash
# Generate với validation loop (tự động)
python scripts/generate_with_validation.py template.md output/

# Output:
# Iteration 1: Found 3 errors
#   - Module "Helmet Detection": Purpose is empty
#   - Module "Vest Detection": Alert Logic is empty
#   - Missing section: System Requirements
# 
# Iteration 2: Found 1 error
#   - Module "Helmet Detection": Purpose is empty
# 
# Iteration 3: Validation PASSED! ✅
```

## Next Steps

1. ✅ Implement Subagent 2 (validation logic)
2. ✅ Implement main orchestrator với loop
3. ✅ Test với real templates
4. ✅ Refine validation rules



