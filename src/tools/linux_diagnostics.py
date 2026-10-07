import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any
from src.core.config import settings
from src.core.logger import logger


@dataclass
class ToolExecutionResult:
    tool_name: str
    success: bool
    output: str
    error: str | None = None
    exit_code: int = 0


class LinuxDiagnostics:
    """Safe, read-only Linux system inspection and diagnostic tools."""

    def __init__(self, timeout_seconds: int = settings.tool_timeout_seconds):
        self.timeout = timeout_seconds

    def _run_command(self, cmd: list[str], tool_name: str) -> ToolExecutionResult:
        """Run a command safely without shell=True to prevent injection."""
        binary = cmd[0]
        if not shutil.which(binary):
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=f"Command '{binary}' is not available on this system.",
                exit_code=127
            )

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )
            output = res.stdout.strip()
            if not output and res.stderr:
                output = res.stderr.strip()

            return ToolExecutionResult(
                tool_name=tool_name,
                success=(res.returncode == 0 or bool(output)),
                output=output if output else "(No output)",
                error=res.stderr.strip() if res.returncode != 0 and res.stderr else None,
                exit_code=res.returncode
            )
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=f"Command '{' '.join(cmd)}' timed out after {self.timeout}s.",
                exit_code=124
            )
        except Exception as e:
            logger.error(f"Error executing diagnostic tool {tool_name}: {e}")
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )

    def get_system_overview(self) -> ToolExecutionResult:
        """Collect high-level system metrics (Uptime, Load, Memory, Disk)."""
        metrics = []

        # Uptime / Load
        uptime_res = self._run_command(["uptime"], "uptime")
        if uptime_res.success:
            metrics.append(f"=== Uptime & Load ===\n{uptime_res.output}")

        # Memory usage
        free_res = self._run_command(["free", "-h"], "free")
        if free_res.success:
            metrics.append(f"=== Memory Usage ===\n{free_res.output}")

        # Disk space
        df_res = self._run_command(["df", "-h", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs"], "df")
        if df_res.success:
            metrics.append(f"=== Disk Space Usage ===\n{df_res.output}")

        # OS Information
        uname_res = self._run_command(["uname", "-srmo"], "uname")
        if uname_res.success:
            metrics.append(f"=== Kernel & Architecture ===\n{uname_res.output}")

        return ToolExecutionResult(
            tool_name="get_system_overview",
            success=True,
            output="\n\n".join(metrics)
        )

    def check_service_status(self, service_name: str) -> ToolExecutionResult:
        """Inspect a systemd service status and its recent log output."""
        # Sanitize service name to prevent invalid input
        clean_name = service_name.strip()
        if not re.match(r"^[a-zA-Z0-9@_.-]+$", clean_name):
            return ToolExecutionResult(
                tool_name="check_service_status",
                success=False,
                output="",
                error=f"Invalid service name format: '{clean_name}'",
                exit_code=1
            )

        # systemctl status
        status_res = self._run_command(
            ["systemctl", "status", clean_name, "--no-pager", "-l"],
            "systemctl_status"
        )

        # journalctl recent logs
        logs_res = self._run_command(
            ["journalctl", "-u", clean_name, "-n", "25", "--no-pager"],
            "journalctl_service"
        )

        combined = f"=== Service Status: {clean_name} ===\n{status_res.output}\n\n=== Recent Journal Logs (last 25 entries) ===\n{logs_res.output}"

        return ToolExecutionResult(
            tool_name="check_service_status",
            success=status_res.success or logs_res.success,
            output=combined,
            exit_code=status_res.exit_code
        )

    def check_network_ports(self, filter_term: str = "") -> ToolExecutionResult:
        """List active listening network ports and bound processes."""
        cmd = ["ss", "-tulpn"]
        res = self._run_command(cmd, "check_network_ports")
        if not res.success and shutil.which("netstat"):
            res = self._run_command(["netstat", "-tuln"], "check_network_ports")

        if filter_term and res.success:
            clean_term = filter_term.lower()
            lines = [line for line in res.output.splitlines() if clean_term in line.lower() or "State" in line or "Proto" in line]
            filtered_output = "\n".join(lines) if lines else f"No listening ports found matching '{filter_term}'"
            return ToolExecutionResult(
                tool_name="check_network_ports",
                success=True,
                output=filtered_output
            )

        return res

    def check_journal_errors(self, lines: int = 30) -> ToolExecutionResult:
        """Retrieve recent critical/error log entries from systemd journal."""
        count = min(max(lines, 5), 100)
        return self._run_command(
            ["journalctl", "-p", "err..emerg", "-n", str(count), "--no-pager"],
            "check_journal_errors"
        )

    def check_disk_inodes(self) -> ToolExecutionResult:
        """Check filesystem inode usage to detect inode exhaustion."""
        return self._run_command(
            ["df", "-i", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs"],
            "check_disk_inodes"
        )

    def check_oom_events(self) -> ToolExecutionResult:
        """Search dmesg and kernel logs for Out Of Memory (OOM) killer events."""
        res = self._run_command(
            ["journalctl", "-k", "-g", "oom|Out of memory|killed process", "-n", "20", "--no-pager"],
            "check_oom_events"
        )
        if not res.success or "(No output)" in res.output or not res.output.strip():
            # Try dmesg if journalctl returned nothing
            dmesg_res = self._run_command(["dmesg", "-T"], "dmesg")
            if dmesg_res.success:
                oom_lines = [
                    line for line in dmesg_res.output.splitlines()
                    if any(k in line.lower() for k in ["oom", "out of memory", "killed process"])
                ]
                output = "\n".join(oom_lines[-20:]) if oom_lines else "No OOM killer events detected in recent kernel logs."
                return ToolExecutionResult(
                    tool_name="check_oom_events",
                    success=True,
                    output=output
                )
            return ToolExecutionResult(
                tool_name="check_oom_events",
                success=True,
                output="No OOM killer events detected."
            )
        return res


# Global instance
diagnostics = LinuxDiagnostics()
