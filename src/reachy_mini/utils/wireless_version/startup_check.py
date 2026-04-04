"""Check and fix ownership of files under /venvs directory.

This module ensures that all files under /venvs are owned by the pollen user.
If any files are not owned by pollen, it will recursively change ownership.

Note: This module only works on Linux/Unix systems. On Windows, the functions
are no-ops.
"""

import logging
import platform
import subprocess
from pathlib import Path

# pwd module is only available on Unix systems
if platform.system() != "Windows":
    import pwd
else:
    pwd = None  # type: ignore

logger = logging.getLogger(__name__)
USER = "pollen"


def check_and_fix_venvs_ownership(
    venvs_path: str = "/venvs", custom_logger: logging.Logger | None = None
) -> None:
    """Check if files under venvs_path are owned by user pollen and fix if needed.

    Args:
        venvs_path: Path to the virtual environments directory (default: /venvs)
        custom_logger: Optional logger to use instead of the module logger

    """
    # This function only works on Unix systems
    if platform.system() == "Windows" or pwd is None:
        return

    try:
        # Get pollen user's UID
        pollen_uid = pwd.getpwnam(USER).pw_uid
    except KeyError:
        print(f"User '{USER}' does not exist on this system")
        return

    venvs_dir = Path(venvs_path)

    if not venvs_dir.exists():
        print(f"Directory {venvs_path} does not exist")
        return

    if not venvs_dir.is_dir():
        print(f"{venvs_path} exists but is not a directory")
        return

    # Check if any files are not owned by pollen
    needs_fix = False
    try:
        for item in venvs_dir.rglob("*"):
            try:
                if item.stat().st_uid != pollen_uid:
                    needs_fix = True
                    print(f"Found file not owned by {USER}: {item}")
                    break
            except (PermissionError, OSError) as e:
                print(f"Cannot check ownership of {item}: {e}")
    except (PermissionError, OSError) as e:
        print(f"Cannot access {venvs_path}: {e}")
        return

    if needs_fix:
        print(f"Fixing ownership of {venvs_path} to {USER}:{USER}")
        try:
            # Run chown with sudo to fix ownership
            subprocess.run(
                ["sudo", "chown", f"{USER}:{USER}", "-R", venvs_path],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Successfully fixed ownership of {venvs_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to fix ownership: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error while fixing ownership: {e}")
    else:
        print(f"All files under {venvs_path} are owned by {USER}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_and_fix_venvs_ownership()
