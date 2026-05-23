"""Application factory tests."""

from app.main import create_app


def test_create_app_builds_routes() -> None:
    app = create_app()
    paths = {route.path for route in app.router.routes if hasattr(route, "path")}

    assert app is not None
    assert paths
    assert "/" in paths
    assert "/healthz" in paths
    assert "/api/v1/games" in paths
    assert "/api/v1/ws/{player_id}" in paths
