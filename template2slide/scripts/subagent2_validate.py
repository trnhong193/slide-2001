#!/usr/bin/env python3
"""
Subagent 2: Review & Validate Slides
Compares generated slides with original template .md file
Checks for errors and generates validation report
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Import ProposalParser from map_to_slides for consistency
sys.path.insert(0, str(Path(__file__).parent))
from map_to_slides import ProposalParser, REGEX_PATTERNS


@dataclass
class ValidationError:
    """Represents a validation error"""
    type: str  # 'critical' or 'warning'
    category: str  # 'module', 'section', 'field', 'architecture', etc.
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation"""
    passed: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors"""
        return any(e.type == 'critical' for e in self.errors)
    
    def total_issues(self) -> int:
        """Total number of issues (errors + warnings)"""
        return len(self.errors) + len(self.warnings)


class SlideValidator:
    """Validate generated slides against template"""
    
    def __init__(self, template_file: str, slide_structure_file: str):
        self.template_file = Path(template_file)
        self.slide_structure_file = Path(slide_structure_file)
        
        # Parse template
        self.template_parser = ProposalParser(str(self.template_file))
        self.template_data = self.template_parser.parse()
        
        # Load slide structure
        with open(self.slide_structure_file, 'r', encoding='utf-8') as f:
            self.slide_structure = json.load(f)
    
    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        result = ValidationResult(passed=True)
        
        # Run all validation checks
        self._validate_content_completeness(result)
        self._validate_module_information(result)
        self._validate_field_extraction(result)
        self._validate_architecture(result)
        self._validate_format_consistency(result)
        
        # Determine if passed
        result.passed = not result.has_critical_errors()
        
        return result
    
    def _validate_content_completeness(self, result: ValidationResult):
        """Check if all template sections are mapped to slides"""
        template_sections = set(self.template_data['sections'].keys())
        
        # Expected sections that should be in slides
        required_sections = {
            "1. COVER PAGE",
            "2. PROJECT REQUIREMENT STATEMENT",
            "3. SCOPE OF WORK",
            "4. SYSTEM ARCHITECTURE",
            "5. SYSTEM REQUIREMENTS",
            "6. IMPLEMENTATION PLAN (TIMELINE)",
            "7. PROPOSED MODULES & FUNCTIONAL DESCRIPTION"
        }
        
        # Check if required sections exist in template
        missing_in_template = required_sections - template_sections
        if missing_in_template:
            for section in missing_in_template:
                result.errors.append(ValidationError(
                    type='critical',
                    category='section',
                    message=f"Required section missing in template: {section}",
                    details={'section': section}
                ))
        
        # Check slide structure has expected slides
        slides = self.slide_structure.get('slides', [])
        if not slides:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="No slides found in slide structure",
                details={}
            ))
            return
        
        # Check for cover page slide
        has_cover = any(s.get('type') == 'title' for s in slides)
        if not has_cover:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="Cover page slide (title) missing",
                details={}
            ))
        
        # Check for project requirement slide
        has_project_req = any(
            s.get('type') == 'content_bullets' and 
            'Project Requirement' in s.get('title', '')
            for s in slides
        )
        if not has_project_req:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="Project Requirement Statement slide missing",
                details={}
            ))
        
        # Check for scope of work slide
        has_scope = any(
            s.get('type') == 'two_column' and 
            'Scope' in s.get('title', '')
            for s in slides
        )
        if not has_scope:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="Scope of Work slide missing",
                details={}
            ))
        
        # Check for architecture slide
        has_architecture = any(
            s.get('type') == 'diagram' and 
            'Architecture' in s.get('title', '')
            for s in slides
        )
        if not has_architecture:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="System Architecture slide missing",
                details={}
            ))
        
        # Check for timeline slide
        has_timeline = any(s.get('type') == 'timeline' for s in slides)
        if not has_timeline:
            result.errors.append(ValidationError(
                type='critical',
                category='content',
                message="Implementation Plan (Timeline) slide missing",
                details={}
            ))
    
    def _validate_module_information(self, result: ValidationResult):
        """Validate module information completeness"""
        # Extract modules from template
        template_modules = self._extract_modules_from_template()
        
        # Extract modules from slides
        slide_modules = self._extract_modules_from_slides()
        
        # Check if all template modules are in slides
        template_module_names = {m['name'].lower() for m in template_modules if m.get('name')}
        slide_module_names = {m['name'].lower() for m in slide_modules if m.get('name')}
        
        missing_modules = template_module_names - slide_module_names
        if missing_modules:
            for module_name in missing_modules:
                result.errors.append(ValidationError(
                    type='critical',
                    category='module',
                    message=f"Module from template not found in slides: {module_name}",
                    details={'module_name': module_name}
                ))
        
        # Validate each module slide
        for module in slide_modules:
            module_name = module.get('name', 'Unknown')
            
            # Check required fields
            required_fields = {
                'purpose': 'Purpose Description',
                'alert_logic': 'Alert Trigger Logic',
                'preconditions': 'Preconditions'
            }
            
            for field_key, field_name in required_fields.items():
                value = module.get(field_key, '').strip()
                if not value:
                    result.errors.append(ValidationError(
                        type='critical',
                        category='module',
                        message=f"Module '{module_name}': {field_name} is empty",
                        details={
                            'module_name': module_name,
                            'field': field_name,
                            'field_key': field_key
                        }
                    ))
            
            # Check module type
            module_type = module.get('type', '').strip()
            if not module_type:
                result.warnings.append(ValidationError(
                    type='warning',
                    category='module',
                    message=f"Module '{module_name}': Module Type is empty",
                    details={'module_name': module_name}
                ))
            
            # Optional fields (warnings only)
            image_url = module.get('_image_url', '').strip()
            video_url = module.get('_video_url', '').strip()
            # These are optional, so no error if empty
    
    def _validate_field_extraction(self, result: ValidationResult):
        """Validate field extraction from Project Requirement Statement"""
        project_req_section = self.template_data['sections'].get(
            "2. PROJECT REQUIREMENT STATEMENT", ""
        )
        
        if not project_req_section:
            return  # Already checked in content completeness
        
        # Extract fields from template
        from map_to_slides import SlideMapper
        mapper = SlideMapper(self.template_data, None)
        template_fields = mapper._extract_key_value_pairs(project_req_section)
        
        # Find project requirement slide
        project_req_slide = None
        for slide in self.slide_structure.get('slides', []):
            if (slide.get('type') == 'content_bullets' and 
                'Project Requirement' in slide.get('title', '')):
                project_req_slide = slide
                break
        
        if not project_req_slide:
            return  # Already checked in content completeness
        
        # Check if key fields are present
        required_fields = ['Project', 'Project Owner', 'Camera Number']
        slide_content = project_req_slide.get('content', [])
        slide_text = ' '.join([item.get('text', '') for item in slide_content])
        
        for field in required_fields:
            if field.lower() not in slide_text.lower():
                result.errors.append(ValidationError(
                    type='critical',
                    category='field',
                    message=f"Required field '{field}' not found in Project Requirement slide",
                    details={'field': field}
                ))
    
    def _validate_architecture(self, result: ValidationResult):
        """Validate architecture diagram"""
        # Find architecture slide
        arch_slide = None
        for slide in self.slide_structure.get('slides', []):
            if slide.get('type') == 'diagram' and 'Architecture' in slide.get('title', ''):
                arch_slide = slide
                break
        
        if not arch_slide:
            return  # Already checked in content completeness
        
        # Check if diagram code exists
        diagram = arch_slide.get('diagram', {})
        diagram_code = diagram.get('code', '').strip()
        
        if not diagram_code:
            result.errors.append(ValidationError(
                type='critical',
                category='architecture',
                message="Architecture diagram code is empty",
                details={}
            ))
        else:
            # Check if it's valid Mermaid code
            if not diagram_code.startswith('graph') and not diagram_code.startswith('flowchart'):
                result.warnings.append(ValidationError(
                    type='warning',
                    category='architecture',
                    message="Architecture diagram may not be valid Mermaid code",
                    details={'code_preview': diagram_code[:100]}
                ))
    
    def _validate_format_consistency(self, result: ValidationResult):
        """Validate format consistency"""
        slides = self.slide_structure.get('slides', [])
        
        # Check slide numbering
        expected_numbers = list(range(1, len(slides) + 1))
        actual_numbers = [s.get('slide_number', 0) for s in slides]
        
        if sorted(actual_numbers) != expected_numbers:
            result.errors.append(ValidationError(
                type='critical',
                category='format',
                message="Slide numbering is not continuous",
                details={
                    'expected': expected_numbers,
                    'actual': actual_numbers
                }
            ))
        
        # Check for duplicate slide numbers
        seen_numbers = {}
        for slide in slides:
            num = slide.get('slide_number', 0)
            if num in seen_numbers:
                result.errors.append(ValidationError(
                    type='critical',
                    category='format',
                    message=f"Duplicate slide number: {num}",
                    details={
                        'slide_number': num,
                        'first_slide': seen_numbers[num],
                        'duplicate_slide': slide.get('title', 'Unknown')
                    }
                ))
            seen_numbers[num] = slide.get('title', 'Unknown')
    
    def _extract_modules_from_template(self) -> List[Dict[str, Any]]:
        """Extract modules from template"""
        modules_section = self.template_data['sections'].get(
            "7. PROPOSED MODULES & FUNCTIONAL DESCRIPTION", ""
        )
        
        if not modules_section:
            return []
        
        # Use SlideMapper to extract modules (reuse existing logic)
        from map_to_slides import SlideMapper
        mapper = SlideMapper(self.template_data, None)
        modules = mapper._extract_modules(modules_section)
        
        return modules
    
    def _extract_modules_from_slides(self) -> List[Dict[str, Any]]:
        """Extract modules from slide structure"""
        modules = []
        
        for slide in self.slide_structure.get('slides', []):
            if slide.get('type') == 'module_description':
                module = {
                    'name': slide.get('title', ''),
                    'type': slide.get('module_type', ''),
                    'purpose': slide.get('content', {}).get('purpose', ''),
                    'alert_logic': slide.get('content', {}).get('alert_logic', ''),
                    'preconditions': slide.get('content', {}).get('preconditions', ''),
                    '_image_url': slide.get('_image_url', ''),
                    '_video_url': slide.get('_video_url', '')
                }
                modules.append(module)
        
        return modules


def validate_slides(template_file: str, slide_structure_file: str) -> ValidationResult:
    """
    Main function to validate slides against template
    
    Args:
        template_file: Path to original template .md file
        slide_structure_file: Path to generated slide structure JSON
    
    Returns:
        ValidationResult with errors and warnings
    """
    validator = SlideValidator(template_file, slide_structure_file)
    return validator.validate()


def print_validation_report(result: ValidationResult):
    """Print validation report to console"""
    print("\n" + "="*80)
    print("VALIDATION REPORT")
    print("="*80)
    
    if result.passed:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
    
    print(f"\nTotal Issues: {result.total_issues()}")
    print(f"  - Critical Errors: {len(result.errors)}")
    print(f"  - Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\n" + "-"*80)
        print("CRITICAL ERRORS:")
        print("-"*80)
        for i, error in enumerate(result.errors, 1):
            print(f"\n{i}. [{error.category.upper()}] {error.message}")
            if error.details:
                for key, value in error.details.items():
                    print(f"   {key}: {value}")
    
    if result.warnings:
        print("\n" + "-"*80)
        print("WARNINGS:")
        print("-"*80)
        for i, warning in enumerate(result.warnings, 1):
            print(f"\n{i}. [{warning.category.upper()}] {warning.message}")
            if warning.details:
                for key, value in warning.details.items():
                    print(f"   {key}: {value}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python subagent2_validate.py <template_file.md> <slide_structure.json>")
        sys.exit(1)
    
    template_file = sys.argv[1]
    slide_structure_file = sys.argv[2]
    
    # Validate
    result = validate_slides(template_file, slide_structure_file)
    
    # Print report
    print_validation_report(result)
    
    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)



