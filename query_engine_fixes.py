#!/usr/bin/env python3
"""
Query Engine Fixes for Large-Scale Downloads

Apply critical fixes to query_engine.py to improve reliability during massive downloads.
"""

import re
import sys


def apply_query_engine_fixes():
    """Apply critical fixes to the query engine for large-scale downloads"""

    query_engine_path = "src/snowpylot/query_engine.py"

    print("🔧 Applying critical fixes to query_engine.py...")

    try:
        # Read the current file
        with open(query_engine_path, "r") as f:
            content = f.read()

        # Fix 1: DryRunResult __str__ method null check
        content = content.replace(
            'def __str__(self) -> str:\n        """Return a formatted dry run string"""\n        return (\n            f"Dry Run Result:\\n"\n            f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\\n"\n            f"  State: {self.query_filter.state or \'Any\'}\\n"\n            f"  Username: {self.query_filter.username or \'Any\'}\\n"\n            f"  Organization: {self.query_filter.organization_name or \'Any\'}\\n"\n            f"  Total pits: {self.total_pits}\\n"\n            f"  Format: CAAML"\n        )',
            'def __str__(self) -> str:\n        """Return a formatted dry run string"""\n        if self.query_filter is None:\n            return "Dry Run Result: No query filter specified"\n        \n        return (\n            f"Dry Run Result:\\n"\n            f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\\n"\n            f"  State: {self.query_filter.state or \'Any\'}\\n"\n            f"  Username: {self.query_filter.username or \'Any\'}\\n"\n            f"  Organization: {self.query_filter.organization_name or \'Any\'}\\n"\n            f"  Total pits: {self.total_pits}\\n"\n            f"  Format: CAAML"\n        )',
        )

        # Fix 2: _extract_form_build_id return type
        content = content.replace(
            "return None",
            'return ""',
            1,  # Only replace the first occurrence in _extract_form_build_id
        )

        # Fix 3: Add error handling for per_page limit validation
        if (
            "def download_results(" in content
            and "MAX_PER_PAGE_WARNING = 1000" not in content
        ):
            # Add a constant for large per_page warnings
            content = content.replace(
                "RESULTS_PER_PAGE = 100  # default number of results per page (max allowed by API: 100)",
                "RESULTS_PER_PAGE = 100  # default number of results per page (max allowed by API: 100)\nMAX_PER_PAGE_WARNING = 1000  # warn if per_page is suspiciously high",
            )

        # Fix 4: Add better error handling for date parsing
        content = content.replace(
            'if isinstance(date_input, str):\n            # Validate string format\n            try:\n                datetime.strptime(date_input, "%Y-%m-%d")\n                return date_input\n            except ValueError:\n                raise ValueError(\n                    f"Invalid date string format: {date_input}. Use YYYY-MM-DD format."\n                )',
            'if isinstance(date_input, str):\n            # Validate string format\n            try:\n                datetime.strptime(date_input, "%Y-%m-%d")\n                return date_input\n            except ValueError:\n                # Try to extract just the date part if it contains time info\n                if " " in date_input:\n                    date_part = date_input.split(" ")[0]\n                    try:\n                        datetime.strptime(date_part, "%Y-%m-%d")\n                        return date_part\n                    except ValueError:\n                        pass\n                raise ValueError(\n                    f"Invalid date string format: {date_input}. Use YYYY-MM-DD format."\n                )',
        )

        # Save the modified content
        with open(query_engine_path, "w") as f:
            f.write(content)

        print("✅ Fixes applied successfully!")

    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    apply_query_engine_fixes()
