import re
from dataclasses import dataclass
from typing import Any


@dataclass
class RoutingDecision:
    intent: str
    target_service: str | None
    target_port: str | None
    tools_to_run: list[tuple[str, dict[str, Any]]]  # (tool_name, kwargs)
    search_query: str


class QueryRouter:
    """Classifies user queries into diagnostic categories and selects safe tools to execute."""

    # Common Linux services
    KNOWN_SERVICES = [
        "nginx", "apache2", "httpd", "caddy", "docker", "containerd", "podman",
        "mysql", "mariadb", "postgresql", "postgres", "redis", "mongodb",
        "ssh", "sshd", "systemd-resolved", "ufw", "firewalld", "cron", "crond"
    ]

    def route(self, query: str) -> RoutingDecision:
        query_lower = query.lower()
        tools: list[tuple[str, dict[str, Any]]] = []
        target_service = None
        target_port = None

        # 1. Check for specific service mentions
        for svc in self.KNOWN_SERVICES:
            if re.search(rf"\b{svc}\b", query_lower):
                target_service = svc
                break

        # 2. Check for port patterns
        port_match = re.search(r"\bport\s*(\d{2,5})\b", query_lower) or re.search(r":(\d{2,5})\b", query_lower)
        if port_match:
            target_port = port_match.group(1)

        # 3. Intent Detection & Tool Selection
        if any(w in query_lower for w in ["system status", "health check", "overview", "load", "cpu usage", "system resources"]):
            intent = "system_overview"
            tools.append(("get_system_overview", {}))

        elif target_service or any(w in query_lower for w in ["service", "systemctl", "failed to start", "status=", "203/exec", "exit code"]):
            intent = "service_troubleshoot"
            if target_service:
                tools.append(("check_service_status", {"service_name": target_service}))
            else:
                tools.append(("check_journal_errors", {"lines": 25}))

        elif target_port or any(w in query_lower for w in ["port", "address already in use", "listening", "econnrefused", "connection refused", "dns", "resolve"]):
            intent = "network_troubleshoot"
            tools.append(("check_network_ports", {"filter_term": target_port or ""}))

        elif any(w in query_lower for w in ["oom", "out of memory", "killed process", "memory leak", "swap"]):
            intent = "memory_troubleshoot"
            tools.append(("check_oom_events", {}))
            tools.append(("get_system_overview", {}))

        elif any(w in query_lower for w in ["disk full", "no space", "inodes", "read-only", "filesystem", "df -h"]):
            intent = "storage_troubleshoot"
            tools.append(("check_disk_inodes", {}))
            tools.append(("get_system_overview", {}))

        else:
            intent = "general_query"

        # Search query enhancement with extracted service or error codes
        search_query = query
        if target_service and target_service not in search_query:
            search_query = f"{target_service} {search_query}"

        return RoutingDecision(
            intent=intent,
            target_service=target_service,
            target_port=target_port,
            tools_to_run=tools,
            search_query=search_query
        )


router = QueryRouter()
