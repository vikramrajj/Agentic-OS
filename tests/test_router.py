from src.agent.router import QueryRouter


def test_router_service_detection():
    router = QueryRouter()
    decision = router.route("My nginx service failed with exit code 1")
    assert decision.intent == "service_troubleshoot"
    assert decision.target_service == "nginx"
    tool_names = [t[0] for t in decision.tools_to_run]
    assert "check_service_status" in tool_names


def test_router_network_port_detection():
    router = QueryRouter()
    decision = router.route("Why is address already in use on port 8080?")
    assert decision.intent == "network_troubleshoot"
    assert decision.target_port == "8080"
    tool_names = [t[0] for t in decision.tools_to_run]
    assert "check_network_ports" in tool_names


def test_router_oom_detection():
    router = QueryRouter()
    decision = router.route("My application was killed by OOM killer")
    assert decision.intent == "memory_troubleshoot"
    tool_names = [t[0] for t in decision.tools_to_run]
    assert "check_oom_events" in tool_names


def test_router_system_overview():
    router = QueryRouter()
    decision = router.route("Give me a system status overview and CPU load")
    assert decision.intent == "system_overview"
    tool_names = [t[0] for t in decision.tools_to_run]
    assert "get_system_overview" in tool_names
