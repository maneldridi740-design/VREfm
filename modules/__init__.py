# ============================================================
# Cell 2 — Create module folder
# ============================================================
import os

os.makedirs("/content/modules", exist_ok=True)

with open("/content/modules/__init__.py", "w") as fh:
    fh.write("")

print("modules/ folder created")
