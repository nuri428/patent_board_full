from fastapi.routing import APIRoute

from app.main import app


def _route_index() -> dict[tuple[str, str], APIRoute]:
    routes: dict[tuple[str, str], APIRoute] = {}
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                routes[(method, route.path)] = route
    return routes


def test_new_feature_routes_are_registered() -> None:
    routes = _route_index()

    expected = {
        ("POST", "/api/v1/cleanup/trigger"),
        ("GET", "/api/v1/cleanup/stats"),
        ("GET", "/api/v1/cleanup/config"),
        ("PUT", "/api/v1/cleanup/config"),
        ("GET", "/api/v1/cleanup/health"),
        ("POST", "/api/v1/session-favorites"),
        ("GET", "/api/v1/session-favorites"),
        ("GET", "/api/v1/session-favorites/search"),
        ("GET", "/api/v1/session-favorites/{favorite_id}"),
        ("PUT", "/api/v1/session-favorites/{favorite_id}"),
        ("DELETE", "/api/v1/session-favorites/{favorite_id}"),
        ("POST", "/api/v1/session-favorites/{favorite_id}/pin"),
        ("POST", "/api/v1/multi-modal"),
        ("POST", "/api/v1/patents/search"),
        ("POST", "/api/v1/patent-country/search"),
    }

    missing = sorted([f"{method} {path}" for method, path in expected if (method, path) not in routes])
    assert not missing, f"Missing routes: {missing}"


def test_session_group_routes_are_registered() -> None:
    routes = _route_index()

    expected = {
        ("POST", "/api/v1/session-groups"),
        ("GET", "/api/v1/session-groups"),
        ("GET", "/api/v1/session-groups/{group_id}"),
        ("PUT", "/api/v1/session-groups/{group_id}"),
        ("DELETE", "/api/v1/session-groups/{group_id}"),
        ("GET", "/api/v1/session-groups/user/groups"),
        ("POST", "/api/v1/session-groups/{group_id}/members/{user_id}"),
        ("DELETE", "/api/v1/session-groups/{group_id}/members/{user_id}"),
        ("GET", "/api/v1/session-groups/{group_id}/members"),
        ("POST", "/api/v1/session-groups/tags"),
    }

    missing = sorted([f"{method} {path}" for method, path in expected if (method, path) not in routes])
    assert not missing, f"Missing routes: {missing}"
