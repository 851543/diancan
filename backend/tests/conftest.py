import sys
from pathlib import Path

# 保证无论从哪启动 pytest / 直接运行测试文件，都能 import app
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
