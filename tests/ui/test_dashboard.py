
"""Browser smoke tests for the MiniPay dashboard."""

from playwright.sync_api import Page, expect


def test_dashboard_loads(page: Page):
    """Verify that the dashboard opens successfully."""
    response = page.goto("http://127.0.0.1:8000/")

    assert response is not None
    assert response.status == 200

    expect(page).to_have_title("MiniPay Dashboard")
    expect(page.get_by_role("heading", name="MiniPay Dashboard")).to_be_visible()


def test_dashboard_contains_required_sections(page: Page):
    """Verify that customer, payment, and search sections are available."""
    page.goto("http://127.0.0.1:8000/")

    expect(page.get_by_role("heading", name="Create Customer")).to_be_visible()
    expect(page.get_by_role("heading", name="Submit Payment")).to_be_visible()
    expect(page.get_by_role("heading", name="Search Transaction")).to_be_visible()


def test_dashboard_contains_api_key_field(page: Page):
    """Verify that the merchant API key field is present."""
    page.goto("http://127.0.0.1:8000/")

    expect(page.locator("#apiKey")).to_be_visible()
    expect(page.locator("#apiKey")).to_have_attribute("type", "password")
