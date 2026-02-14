#!/usr/bin/env python3
"""
Master Content Pipeline
Orchestrates: Generation -> Audit -> Internal Linking -> Resource Optimization
One command to rule them all.
"""
import subprocess
import sys
import os
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def run_script(script_name, args=None):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    print(f"\n🚀 Running: {' '.join(cmd)}...")
    try:
        subprocess.check_call(cmd, cwd=str(PROJECT_ROOT))
        print(f"✅ Completed: {script_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {script_name} (Exit code: {e.returncode})")
        # Exit if critical stages fail (Audit/Link/Optimize)
        # We can be more lenient with generation scripts if they fail partially
        if script_name not in ["generate_2026_hot_topics.py", "generate_gsc_targeted_articles.py"]:
            print(f"🛑 Critical stage failed. Stopping pipeline.")
            sys.exit(e.returncode)
        return False

def main():
    print("=" * 60)
    print("🌟 STARGAZER CONTENT PIPELINE - AI CODING FLOW 2026")
    print("=" * 60)

    # 1. Content Generation
    print("\n--- STAGE 1: Content Generation ---")
    # We run generation scripts. These are safe to run even if articles exist (they skip existing slugs)
    run_script("generate_2026_hot_topics.py")
    run_script("generate_gsc_targeted_articles.py")

    # 2. Tech Audit & Formatting Fix
    print("\n--- STAGE 2: Formatting Audit & Auto-Fix ---")
    # This ensures no AI filler or code block wrappers remain
    run_script("audit_article_formatting.py", ["--fix"])

    # 3. Internal Link Building
    print("\n--- STAGE 3: SEO Link Building ---")
    run_script("internal_link_builder.py")

    # 4. Asset Optimization
    print("\n--- STAGE 4: Image Optimization (WebP) ---")
    run_script("optimize_assets.py")

    print("\n" + "=" * 60)
    print("🎉 Pipeline Execution Complete!")
    print("Next suggested step: Run 'npm run build' or 'git commit'")
    print("=" * 60)

if __name__ == "__main__":
    main()
