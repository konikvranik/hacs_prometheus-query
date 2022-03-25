import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    STATE_UNKNOWN,
)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

DOMAIN = 'prometheus'
CONF_PROMETHEUS_URL = 'prometheus_url'
CONF_PROMETHEUS_QUERY = 'prometheus_query'
SCAN_INTERVAL = timedelta(seconds=600)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PROMETHEUS_URL): cv.string,
    vol.Required(CONF_PROMETHEUS_QUERY): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    prom_data = {
        'url': str(config.get(CONF_PROMETHEUS_URL)) + "/api/v1/query",
        'query': str(config.get(CONF_PROMETHEUS_QUERY)),
        'name': str(config.get(CONF_NAME)),
        'unit': str(config.get(CONF_UNIT_OF_MEASUREMENT)),
    }
    add_entities([PrometheusQuery(prom_data)], True)


class PrometheusQuery(Entity):
    """Representation of a Sensor."""

    def __init__(self, prom_data):
        """Initialize the sensor."""
        self._url = prom_data["url"]
        self._query = prom_data["query"]
        self._name = prom_data["name"]
        self._state = None
        self._unit_of_measurement = prom_data["unit"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        response = requests.get(self._url, params={'query': self._query})
        if (response):
            results = response.json()['data']['result']
            self._state = results[0]['value'][1]
        else:
            self._state = STATE_UNKNOWN
