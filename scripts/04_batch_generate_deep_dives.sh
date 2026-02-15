#!/bin/bash

# 1. Bolt vs Cursor
echo "Generating Bolt vs Cursor..."
python3 scripts/02_unified_content_workflow.py --topic "Bolt vs Cursor Agentic IDE Technical Comparison" --mode general --auto

# 2. Gemini vs Claude
echo "Generating Gemini vs Claude..."
python3 scripts/02_unified_content_workflow.py --topic "Gemini 3 Flash vs Claude Opus 4.6 Technical Benchmark" --mode general --auto

# 3. Ideogram vs Luma
echo "Generating Ideogram vs Luma..."
python3 scripts/02_unified_content_workflow.py --topic "Ideogram 2.0 vs Luma Dream Machine 1.5 Quality Comparison" --mode general --auto

# 4. ChatGPT Atlas Agents
echo "Generating ChatGPT Atlas Guide..."
python3 scripts/02_unified_content_workflow.py --topic "Building Enterprise AI Agent Teams with ChatGPT Atlas" --mode guide --auto

# 5. Tencent Mobile AI
echo "Generating Tencent Mobile AI..."
python3 scripts/02_unified_content_workflow.py --topic "Tencent HY-1.8B-2Bit Architecture Deep Dive" --mode general --auto
