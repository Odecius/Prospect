from fastapi.testclient import TestClient

from app.main import create_app


def test_interface_contains_accessible_navigation_branding_and_operational_controls() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert 'class="skip-link"' in response.text
    assert 'id="search-form"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'alt="ABC Solutions"' in response.text
    assert "Developed by Abc Solutions | Built with quality and care" in response.text
    assert 'id="external-search-form"' in response.text
    assert 'translate="no">Google Maps' in response.text
    assert 'id="website-audit-title"' in response.text
    assert "Não executa JavaScript" in response.text
    assert 'id="ai-draft-title"' in response.text
    assert "Nada é enviado" in response.text


def test_public_transparency_pages_are_available() -> None:
    with TestClient(create_app()) as client:
        privacy = client.get("/privacy")
        terms = client.get("/terms")
    assert privacy.status_code == 200
    assert "Google Places API" in privacy.text
    assert "store=false" in privacy.text
    assert "Política de Privacidade da OpenAI" in privacy.text
    assert terms.status_code == 200
    assert "Termos da Google Maps Platform" in terms.text
    assert "nunca são enviados ou publicados automaticamente" in terms.text
