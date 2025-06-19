#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 import 테스트
"""

try:
    print("BatchCLI import 테스트 중...")
    from cli.batch_cli import BatchCLI
    print("✅ BatchCLI import 성공!")
except Exception as e:
    print(f"❌ BatchCLI import 실패: {e}")
    import traceback
    traceback.print_exc()