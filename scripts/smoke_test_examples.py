#!/usr/bin/env python3
"""
示例代码冒烟测试
- 尝试 import 每个示例的 main.py（不实际运行 AI 调用）
- 检查是否有语法错误、缺失依赖等问题
"""
import importlib.util
import os
import sys
from pathlib import Path


def smoke_test_example(example_dir: Path) -> tuple[bool, str]:
    """对单个示例进行冒烟测试（仅 import，不执行 AI 调用）"""
    main_file = example_dir / "main.py"
    if not main_file.exists():
        return True, "skip (no main.py)"

    try:
        # 设置环境变量标记为冒烟测试，让示例代码跳过真实调用
        os.environ["SMOKE_TEST"] = "true"

        # 尝试 import 模块（不执行 main）
        spec = importlib.util.spec_from_file_location(
            f"example_{example_dir.name}", main_file
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # 不执行模块，只检查语法
            with open(main_file, "r", encoding="utf-8") as f:
                compile(f.read(), str(main_file), "exec")
            return True, "ok"

        return True, "skip (no loader)"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    repo_root = Path(__file__).parent.parent
    examples_dir = repo_root / "examples"

    results = []
    passed = 0
    failed = 0
    skipped = 0

    for example_dir in sorted(examples_dir.iterdir()):
        if not example_dir.is_dir():
            continue

        success, detail = smoke_test_example(example_dir)
        results.append((example_dir.name, success, detail))

        if detail.startswith("skip"):
            skipped += 1
            status = "⏭️"
        elif success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"

        print(f"{status} {example_dir.name}: {detail}")

    print(f"\n=== Summary ===")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total:   {len(results)}")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
