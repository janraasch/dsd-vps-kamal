"""Helper functions specific to VPS Kamal (Hetzner)."""

import json
import subprocess
import time

from tests.e2e_tests.utils.it_helper_functions import make_sp_call


def create_project():
    """Create a Hetzner VPS server for testing.

    Uses active_context and default_ssh_key from ~/.config/hcloud/cli.toml,
    so SSH access works via root@<ip> without extra key setup.
    """
    print("\n\nCreating Hetzner server 'dsdwork'...")
    output = (
        make_sp_call(
            "hcloud server create --name dsdwork --type cx23 --image ubuntu-24.04 --location hel1 --output json",
            capture_output=True,
        )
        .stdout.decode()
        .strip()
    )

    data = json.loads(output)
    server_ip = data["server"]["public_net"]["ipv4"]["ip"]
    print(f"  Server IP: {server_ip}")

    _wait_for_ssh(server_ip)

    return server_ip


def _wait_for_ssh(ip, timeout=120, interval=5):
    """Wait until the server accepts SSH connections."""
    # Remove any stale known_hosts entry for this IP before connecting.
    subprocess.run(["ssh-keygen", "-R", ip], capture_output=True)

    print(f"  Waiting for SSH on {ip}...")
    cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=5",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"root@{ip}",
        "echo",
        "ok",
    ]
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            print("  SSH is ready.")
            return
        time.sleep(interval)
    raise RuntimeError(f"Server at {ip} did not become reachable via SSH within {timeout}s.")


def destroy_project(request):
    """Delete the Hetzner server created for testing."""
    print("\nCleaning up:")

    server_ip = request.config.cache.get("app_name", None)
    if server_ip:
        print(f"  Server IP was: {server_ip}")

    print("  Deleting Hetzner server 'dsdwork'...")
    make_sp_call("hcloud server delete dsdwork")
    print("  Server deleted.")

    if server_ip:
        print(f"  Removing {server_ip} from known_hosts...")
        make_sp_call(f"ssh-keygen -R {server_ip}")
        print("  Done.")


def check_log(tmp_proj_dir):
    """Check the log that was generated during a full deployment.

    Checks that log file exists, and that DATABASE_URL is not logged.
    """
    path = tmp_proj_dir / "dsd_logs"
    if not path.exists():
        return False

    log_files = list(path.glob("dsd_*.log"))
    if not log_files:
        return False

    log_str = log_files[0].read_text()
    if "DATABASE_URL" in log_str:
        return False

    return True
