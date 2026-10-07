import pytest
from src.tools.linux_diagnostics import LinuxDiagnostics, ToolExecutionResult


def test_system_overview():
    diag = LinuxDiagnostics(timeout_seconds=5)
    res = diag.get_system_overview()
    assert isinstance(res, ToolExecutionResult)
    assert res.success is True
    assert "Uptime" in res.output or "Memory" in res.output


def test_service_status_sanitization():
    diag = LinuxDiagnostics(timeout_seconds=5)
    # Test malicious service name with shell injection attempt
    res = diag.check_service_status("nginx; rm -rf /")
    assert res.success is False
    assert "Invalid service name" in (res.error or "")


def test_service_status_valid_format():
    diag = LinuxDiagnostics(timeout_seconds=5)
    # Valid name query (service may or may not be active, but command runs safely)
    res = diag.check_service_status("systemd-resolved")
    assert isinstance(res, ToolExecutionResult)
    assert "Service Status: systemd-resolved" in res.output


def test_network_ports():
    diag = LinuxDiagnostics(timeout_seconds=5)
    res = diag.check_network_ports()
    assert isinstance(res, ToolExecutionResult)
    assert res.success is True


def test_oom_events():
    diag = LinuxDiagnostics(timeout_seconds=5)
    res = diag.check_oom_events()
    assert isinstance(res, ToolExecutionResult)
    assert res.success is True
