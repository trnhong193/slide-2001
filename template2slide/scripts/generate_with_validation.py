#!/usr/bin/env python3
"""
Main Orchestrator: Generate Slides with Automatic Validation Loop
Combines Subagent 1 (Generate) and Subagent 2 (Validate) in iterative loop
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import subagents
from template2slide import generate_architecture, map_to_slides, generate_powerpoint
from subagent2_validate import validate_slides, print_validation_report, ValidationResult


def subagent1_generate(template_file: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Subagent 1: Generate slides from template
    
    Returns:
        Dict with paths to generated files
    """
    print("\n" + "="*80)
    print("SUBAGENT 1: GENERATING SLIDES")
    print("="*80)
    
    try:
        # Step 1: Generate architecture
        arch_file, project_info = generate_architecture(template_file, output_dir)
        
        if not arch_file:
            raise Exception("Architecture generation failed")
        
        # Step 2: Map to slides
        structure_file = map_to_slides(template_file, arch_file, output_dir)
        
        if not structure_file:
            raise Exception("Slide mapping failed")
        
        # Step 3: Generate PowerPoint (optional, may require manual step)
        pptx_file = generate_powerpoint(structure_file, output_dir)
        
        # Convert Path objects to strings for return
        return {
            'success': True,
            'architecture_file': str(arch_file) if arch_file else None,
            'project_info': project_info,
            'structure_file': str(structure_file) if structure_file else None,
            'pptx_file': str(pptx_file) if pptx_file else None
        }
    
    except Exception as e:
        print(f"\n❌ Subagent 1 Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def subagent2_validate(template_file: Path, structure_file: Path) -> ValidationResult:
    """
    Subagent 2: Validate generated slides against template
    
    Returns:
        ValidationResult with errors and warnings
    """
    print("\n" + "="*80)
    print("SUBAGENT 2: VALIDATING SLIDES")
    print("="*80)
    
    try:
        result = validate_slides(str(template_file), str(structure_file))
        return result
    except Exception as e:
        print(f"\n❌ Subagent 2 Error: {e}")
        # Return failed validation result
        from subagent2_validate import ValidationResult, ValidationError
        result = ValidationResult(passed=False)
        result.errors.append(ValidationError(
            type='critical',
            category='validation',
            message=f"Validation process failed: {e}",
            details={'error': str(e)}
        ))
        return result


def generate_slides_with_validation(
    template_file: str,
    output_dir: Optional[str] = None,
    max_iterations: int = 5,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    Main function: Generate slides with automatic validation loop
    
    Args:
        template_file: Path to template .md file
        output_dir: Output directory (default: template directory / output)
        max_iterations: Maximum number of iterations (default: 5)
        auto_fix: Attempt to auto-fix errors (default: False)
    
    Returns:
        Dict with final result and statistics
    """
    template_file = Path(template_file)
    
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    
    # Set output directory
    if output_dir is None:
        output_dir = template_file.parent / "output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("SLIDE GENERATION WITH VALIDATION LOOP")
    print("="*80)
    print(f"Template: {template_file}")
    print(f"Output: {output_dir}")
    print(f"Max Iterations: {max_iterations}")
    print("="*80)
    
    iteration = 0
    all_results = []
    
    while iteration < max_iterations:
        iteration += 1
        
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration}/{max_iterations}")
        print(f"{'='*80}\n")
        
        # Step 1: Generate slides (Subagent 1)
        generate_result = subagent1_generate(template_file, output_dir)
        
        if not generate_result.get('success'):
            error_msg = generate_result.get('error', 'Unknown error')
            print(f"\n❌ Generation failed: {error_msg}")
            all_results.append({
                'iteration': iteration,
                'status': 'generation_failed',
                'error': error_msg
            })
            break
        
        structure_file = generate_result['structure_file']
        
        # Step 2: Validate (Subagent 2)
        validation_result = subagent2_validate(template_file, structure_file)
        
        # Store result
        all_results.append({
            'iteration': iteration,
            'status': 'passed' if validation_result.passed else 'failed',
            'errors': len(validation_result.errors),
            'warnings': len(validation_result.warnings)
        })
        
        # Print validation report
        print_validation_report(validation_result)
        
        # Check if passed
        if validation_result.passed:
            print(f"\n✅ VALIDATION PASSED after {iteration} iteration(s)!")
            print(f"✅ Slides are ready: {structure_file}")
            
            return {
                'success': True,
                'iterations': iteration,
                'structure_file': str(structure_file),
                'pptx_file': str(generate_result.get('pptx_file', '')),
                'architecture_file': str(generate_result.get('architecture_file', '')),
                'all_results': all_results,
                'final_validation': {
                    'passed': True,
                    'errors': len(validation_result.errors),
                    'warnings': len(validation_result.warnings)
                }
            }
        
        # Failed - check if we should continue
        if iteration >= max_iterations:
            print(f"\n❌ MAX ITERATIONS REACHED ({max_iterations})")
            print("❌ Please review template and fix issues manually.")
            
            return {
                'success': False,
                'iterations': iteration,
                'structure_file': str(structure_file),
                'all_results': all_results,
                'final_validation': {
                    'passed': False,
                    'errors': len(validation_result.errors),
                    'warnings': len(validation_result.warnings),
                    'error_list': [
                        {
                            'category': e.category,
                            'message': e.message,
                            'details': e.details
                        }
                        for e in validation_result.errors
                    ]
                }
            }
        
        # Continue to next iteration
        print(f"\n⚠️  Validation failed. Retrying... (iteration {iteration + 1}/{max_iterations})")
        
        # Optional: Attempt auto-fix
        if auto_fix:
            print("🔧 Attempting auto-fix...")
            # Auto-fix logic can be added here
            # For now, just continue to next iteration
    
    # Should not reach here, but just in case
    return {
        'success': False,
        'iterations': iteration,
        'all_results': all_results,
        'error': 'Unexpected loop termination'
    }


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python generate_with_validation.py <template_file.md> [output_dir] [max_iterations]")
        print("\nExample:")
        print("  python generate_with_validation.py template.md output/ 5")
        sys.exit(1)
    
    template_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    try:
        result = generate_slides_with_validation(
            template_file,
            output_dir,
            max_iterations=max_iterations
        )
        
        # Print summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Success: {'✅ YES' if result['success'] else '❌ NO'}")
        print(f"Iterations: {result['iterations']}")
        
        if result['success']:
            print(f"\n✅ Generated Files:")
            print(f"   - Slide Structure: {result.get('structure_file', 'N/A')}")
            print(f"   - Architecture: {result.get('architecture_file', 'N/A')}")
            print(f"   - PowerPoint: {result.get('pptx_file', 'N/A')}")
        else:
            print(f"\n❌ Failed after {result['iterations']} iteration(s)")
            final_val = result.get('final_validation', {})
            if final_val:
                print(f"   - Errors: {final_val.get('errors', 0)}")
                print(f"   - Warnings: {final_val.get('warnings', 0)}")
        
        print("="*80)
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
    
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

