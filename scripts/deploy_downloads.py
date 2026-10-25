"""Upload an already-built publication and activate its isolated Nginx site."""
import argparse
import json
import os
from pathlib import Path
import shlex
import time
import uuid


def deploy(config_path, publish, repository):
    try:
        import paramiko
    except ImportError as exc:
        raise RuntimeError("Deployment only: install paramiko in your development environment first.") from exc
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    password = os.environ.get("SHUJIN_DEPLOY_PASSWORD")
    if not password:
        raise RuntimeError("Set SHUJIN_DEPLOY_PASSWORD to the SSH plaintext password; exported connection passwords may be encrypted.")
    client = paramiko.SSHClient()
    known = repository / ".local/deploy/known_hosts"
    known.parent.mkdir(parents=True, exist_ok=True)
    if known.exists():
        client.load_host_keys(str(known))
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config["host"], port=int(config.get("port", 22)), username=config["user_name"],
                   password=password, look_for_keys=False, allow_agent=False, timeout=20, auth_timeout=20)
    client.save_host_keys(str(known))
    stage = "/tmp/xiaozhu-download-upload-" + uuid.uuid4().hex
    last_notice = [0]
    try:
        with client.open_sftp() as sftp:
            sftp.mkdir(stage, mode=0o700)
            sftp.mkdir(stage + "/publish", mode=0o755)
            for folder in sorted(p for p in publish.rglob("*") if p.is_dir()):
                sftp.mkdir(stage + "/publish/" + folder.relative_to(publish).as_posix(), mode=0o755)
            for source in sorted(p for p in publish.rglob("*") if p.is_file()):
                relative = source.relative_to(publish).as_posix()
                def progress(transferred, total):
                    if total > 1024 * 1024 and (time.monotonic() - last_notice[0] >= 10 or transferred == total):
                        print(json.dumps({"upload": source.name, "percent": round(100 * transferred / total)}), flush=True)
                        last_notice[0] = time.monotonic()
                sftp.put(str(source), stage + "/publish/" + relative, callback=progress)
                print(json.dumps({"uploaded": relative, "bytes": source.stat().st_size}), flush=True)
            sftp.put(str(repository / "scripts/install_downloads.py"), stage + "/install_downloads.py")
            sftp.put(str(repository / "deploy/xiaozhu-downloads.nginx.conf"), stage + "/xiaozhu-downloads.nginx.conf")
        command = "sudo -n /usr/bin/python3 " + shlex.quote(stage + "/install_downloads.py")
        stdin, stdout, stderr = client.exec_command(command, timeout=180)
        output, error = stdout.read().decode(), stderr.read().decode()
        if output:
            print(output, end="", flush=True)
        if error:
            print(error, end="", flush=True)
        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError("Remote installation failed; the upload remains at " + stage)
        # Remove only the exact staging directory created by this invocation.
        cleanup = "sudo -n /usr/bin/python3 -c " + shlex.quote("import shutil; shutil.rmtree(" + repr(stage) + ")")
        stdin, stdout, stderr = client.exec_command(cleanup)
        if stdout.channel.recv_exit_status() != 0:
            print(json.dumps({"cleanupPending": stage}), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--publish", type=Path, default=Path(".local/download-publish"))
    args = parser.parse_args()
    deploy(args.config.resolve(), args.publish.resolve(), Path(__file__).resolve().parents[1])
