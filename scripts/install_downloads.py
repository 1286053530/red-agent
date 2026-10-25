"""Run as root on Linux after uploading publish/ and the Nginx config beside this file."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid


def checksum(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def install(stage):
    if os.geteuid() != 0:
        raise RuntimeError("Run this installer with sudo.")
    publish = stage / "publish"
    manifest = json.loads((publish / "latest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError("Invalid release version")
    root = Path("/srv/xiaozhu-downloads")
    configuration = Path("/etc/nginx/conf.d/xiaozhu-downloads.conf")
    marker = root / ".managed-by-red-agent"
    if root.is_symlink() or configuration.is_symlink():
        raise RuntimeError("Refusing to replace a symlink at the deployment destination")
    if root.exists() and any(root.iterdir()) and not marker.exists():
        raise RuntimeError("The download directory exists and is not managed by this deployment")
    if configuration.exists() and not configuration.read_text().startswith("# Managed download site for red-agent;"):
        raise RuntimeError("An unrelated Nginx configuration already uses this filename")
    listening = subprocess.run(["ss", "-ltnpH", "sport", "=", ":3300"], check=True, capture_output=True, text=True).stdout
    if listening.strip() and (not configuration.exists() or "nginx" not in listening):
        raise RuntimeError("Port 3300 is occupied by an unrelated service")
    subprocess.run(["nginx", "-t"], check=True)
    for item in manifest["downloads"]:
        source = publish / "releases" / version / item["name"]
        if source.stat().st_size != item["size"] or checksum(source) != item["sha256"]:
            raise RuntimeError("Upload checksum mismatch: " + item["name"])
    root.mkdir(mode=0o755, parents=True, exist_ok=True)
    releases = root / "releases"
    releases.mkdir(mode=0o755, exist_ok=True)
    destination = releases / version
    if destination.exists():
        for item in manifest["downloads"]:
            if checksum(destination / item["name"]) != item["sha256"]:
                raise RuntimeError("Refusing to overwrite a published version with different binaries")
    else:
        pending = releases / ("." + version + "-" + uuid.uuid4().hex)
        shutil.copytree(publish / "releases" / version, pending)
        pending.chmod(0o755)
        for path in pending.iterdir():
            path.chmod(0o644)
        pending.rename(destination)
    for name in ["latest.json", "SHA256SUMS.txt", "index.html"]:
        temporary = root / ("." + name + ".tmp")
        shutil.copyfile(publish / name, temporary)
        temporary.chmod(0o644)
        temporary.replace(root / name)
    marker.write_text("Managed by red-agent download deployment.\n")
    marker.chmod(0o644)
    old_configuration = configuration.read_bytes() if configuration.exists() else None
    configuration.write_bytes((stage / "xiaozhu-downloads.nginx.conf").read_bytes())
    configuration.chmod(0o644)
    try:
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
    except Exception:
        if old_configuration is None:
            configuration.unlink(missing_ok=True)
        else:
            configuration.write_bytes(old_configuration)
        raise
    firewall = "inactive_or_unavailable"
    if shutil.which("ufw"):
        status = subprocess.run(["ufw", "status"], check=True, capture_output=True, text=True).stdout
        if "Status: active" in status:
            subprocess.run(["ufw", "allow", "3300/tcp", "comment", "Xiaozhu downloads"], check=True)
            firewall = "3300/tcp allowed"
    print(json.dumps({"installed": True, "version": version, "port": 3300, "root": str(root),
                      "firewall": firewall, "checksumsVerified": True}), flush=True)


if __name__ == "__main__":
    install(Path(__file__).resolve().parent)
