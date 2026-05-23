from __future__ import annotations

import logging
import requests
import datetime

_LOGGER = logging.getLogger(__name__)


class AflasAPI:
    """API client for Aflas.dk."""

    def __init__(
        self,
        username: str,
        password: str,
        vaerknummer: str,
        meter_number: str | None = None,
    ):
        # Store credentials and meter info
        self.username = username
        self.password = password
        self.vaerk = vaerknummer
        self.meter = meter_number  # None when only fetching settings
        self.base = "https://www.aflas.dk"

        # Session is reused for cookies + performance
        self.session = requests.Session()

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------
    def login(self):
        """Perform login and return the raw HTTP response."""
        url = f"{self.base}/{self.vaerk}/login"

        payload = {
            "username": self.username,
            "password": self.password,
            "vaerkNr": self.vaerk,
            "loginIsSecure": "1",
            "reference": "/selvaflaesning/login.php",
        }

        headers = {
            "Referer": f"{self.base}/{self.vaerk}/login",
            "User-Agent": "HomeAssistant Aflas.dk Integration",
        }

        response = self.session.post(url, data=payload, headers=headers, allow_redirects=False)
        _LOGGER.debug(
            "Aflas.dk login response: status=%s location=%s cookies=%s",
            response.status_code,
            response.headers.get("Location"),
            self.session.cookies.get_dict(),
        )

        return response

    # ---------------------------------------------------------
    # LOGIN VALIDATION (used by config-flow + options-flow)
    # ---------------------------------------------------------
    def validate_login(self):
        """
        Validate login credentials.

        Returns:
            True               → Login OK
            "invalid_auth"     → Wrong username/password/vaerknummer
            "cannot_connect"   → Network/server error
        """
        try:
            login_resp = self.login()

            if login_resp.status_code != 302:
                _LOGGER.debug(
                    "Aflas.dk login failed with status %s: %s",
                    login_resp.status_code,
                    login_resp.text[:200],
                )
                return "invalid_auth"

            # Fetch settings to confirm login and meter list
            settings_resp = self.get_settings()
            js = settings_resp.json()
            meters = js.get("maalerNr")

            if isinstance(meters, (str, int)):
                meters = [str(meters)]
            elif meters is None:
                meters = []
            elif not isinstance(meters, list):
                meters = list(meters) if hasattr(meters, "__iter__") else []

            if not meters:
                _LOGGER.debug(
                    "Aflas.dk settings did not contain meters: %s",
                    js,
                )
                return "invalid_auth"

            return True

        except Exception as e:
            _LOGGER.error("Aflas.dk validation error: %s", e)
            return "cannot_connect"

    # ---------------------------------------------------------
    # FETCH SETTINGS (returns meter list)
    # ---------------------------------------------------------
    def get_settings(self):
        """Fetch meter settings. May contain multiple meters."""
        url = f"{self.base}/{self.vaerk}/api?tab=forbrugsettings"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base}/{self.vaerk}/login",
            "User-Agent": "HomeAssistant Aflas.dk Integration",
        }
        response = self.session.get(url, headers=headers, allow_redirects=False)
        _LOGGER.debug(
            "Aflas.dk settings response: status=%s url=%s cookies=%s headers=%s",
            response.status_code,
            response.url,
            self.session.cookies.get_dict(),
            response.request.headers,
        )

        if response.status_code == 302:
            raise Exception(
                "Aflas.dk settings request was redirected, likely missing login/session cookies"
            )

        return response

    # ---------------------------------------------------------
    # FETCH CURRENT USAGE FOR ONE METER
    # ---------------------------------------------------------
    def get_current_usage(self):
        """Fetch current usage (labels + usage arrays) for a specific meter."""
        if not self.meter:
            raise Exception("Meter number not set for usage request")

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        url = (
            f"{self.base}/{self.vaerk}/forbrug?"
            f"type=data&maalerNr={self.meter}&date={today}&view=daily&compare=false"
        )
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base}/{self.vaerk}/login",
            "User-Agent": "HomeAssistant Aflas.dk Integration",
        }

        resp = self.session.get(url, headers=headers, allow_redirects=False)

        if resp.status_code == 302:
            raise Exception(
                "Aflas.dk usage request was redirected, likely invalid login/session"
            )

        if resp.status_code != 200:
            raise Exception(f"Aflas.dk returned HTTP {resp.status_code}")

        try:
            js = resp.json()
        except ValueError as err:
            _LOGGER.error(
                "Aflas.dk usage response was not valid JSON: status=%s url=%s text=%s",
                resp.status_code,
                resp.url,
                resp.text[:500],
            )
            raise

        if "current" not in js:
            raise Exception("Aflas.dk response missing 'current' field")

        return js

    # ---------------------------------------------------------
    # PUBLIC METHOD USED BY COORDINATOR
    # ---------------------------------------------------------
    def get_usage_data(self):
        """
        Full data fetch used by coordinator.
        Handles login + usage fetch for one meter.
        """
        login_resp = self.login()

        if login_resp.status_code != 302:
            raise Exception("Invalid login credentials")

        return self.get_current_usage()

