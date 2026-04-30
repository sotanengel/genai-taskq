from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts" / "dev" / "preflight_ports.sh"
BOOTSTRAP_SCRIPT = REPO_ROOT / "scripts" / "dev" / "bootstrap_launchd.sh"


def _run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(cmd, text=True, capture_output=True, env=merged_env, check=False)


def test_preflight_ports_ok_with_free_port() -> None:
    result = _run(["bash", str(PREFLIGHT_SCRIPT)], env={"GTQ_API_PORT": "48123"})
    assert result.returncode == 0
    assert "available" in result.stdout


def test_preflight_ports_fails_when_port_is_used() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = str(sock.getsockname()[1])
    try:
        result = _run(["bash", str(PREFLIGHT_SCRIPT)], env={"GTQ_API_PORT": port})
    finally:
        sock.close()
    assert result.returncode != 0
    assert "already in use" in result.stderr


def test_bootstrap_launchd_renders_plist_in_dry_run(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    fake_docker = fake_bin / "docker"
    fake_docker.write_text("#!/usr/bin/env bash\necho docker\n", encoding="utf-8")
    fake_docker.chmod(0o755)

    launch_agents_dir = tmp_path / "LaunchAgents"
    workdir = str(REPO_ROOT)
    env = {
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "GTQ_LAUNCHD_DRY_RUN": "1",
        "GTQ_LAUNCH_AGENTS_DIR": str(launch_agents_dir),
        "GTQ_WORKDIR": workdir,
    }
    result = _run(["bash", str(BOOTSTRAP_SCRIPT), "install"], env=env)
    assert result.returncode == 0

    plist_path = launch_agents_dir / "com.genaitaskq.autostart.plist"
    assert plist_path.exists()
    content = plist_path.read_text(encoding="utf-8")
    assert "__WORKDIR__" not in content
    assert workdir in content


def test_bootstrap_launchd_uninstall_removes_plist_in_dry_run(tmp_path: Path) -> None:
    launch_agents_dir = tmp_path / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents_dir / "com.genaitaskq.autostart.plist"
    plist_path.write_text("<plist/>", encoding="utf-8")

    result = _run(
        ["bash", str(BOOTSTRAP_SCRIPT), "uninstall"],
        env={
            "GTQ_LAUNCHD_DRY_RUN": "1",
            "GTQ_LAUNCH_AGENTS_DIR": str(launch_agents_dir),
        },
    )
    assert result.returncode == 0
    assert not plist_path.exists()
