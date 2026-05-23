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

        # Aflas.dk uses 302 redirect on successful login
        return self.session.post(url, data=payload, allow_redirects=False)

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
                return "invalid_auth"

            # Fetch settings to confirm login and meter list
            settings_resp = self.get_settings()

            if settings_resp.status_code != 200:
                return "invalid_auth"

            js = settings_resp.json()
            meters = js.get("maalerNr")

            if not meters or not isinstance(meters, list):
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
        headers = {"X-Requested-With": "XMLHttpRequest"}
        return self.session.get(url, headers=headers)

    # ---------------------------------------------------------
    # FETCH CURRENT USAGE FOR ONE METER
    # ---------------------------------------------------------
    def get_current_usage(self):
        """Fetch current usage (labels + usage arrays) for a specific meter."""
        if not self.meter:
            raise Exception("Meter number not set for usage request")

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        url = (
            f"{self.base}/{self.vaerk}/api?"
            f"tab=forbrugcurrent&maalerNr={self.meter}&date={today}"
        )
        headers = {"X-Requested-With": "XMLHttpRequest"}

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"Aflas.dk returned HTTP {resp.status_code}")

        js = resp.json()

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

