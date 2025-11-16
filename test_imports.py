#!/usr/bin/env python3
"""Test that imports work correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Try to import the bootstrap functions
    from specify_cli import sdd_bootstrap
    
    # Check that the functions exist
    functions_to_check = [
        'create_warpspace',
        'create_or_update_constitution',
        'setup_specs_directory',
        'setup_agent_commands',
        'setup_warp_space_scripts',
        'setup_warp_space_config',
    ]
    
    print("Checking sdd_bootstrap functions:")
    all_exist = True
    for func_name in functions_to_check:
        has_func = hasattr(sdd_bootstrap, func_name)
        status = "✓" if has_func else "✗"
        print(f"  {status} {func_name}")
        if not has_func:
            all_exist = False
    
    if all_exist:
        print("\n✓ All expected functions are present in sdd_bootstrap module")
        sys.exit(0)
    else:
        print("\n✗ Some functions are missing!")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error importing modules: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
