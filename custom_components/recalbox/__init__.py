from homeassistant.core import (
    HomeAssistant,
    CoreState,
    EVENT_HOMEASSISTANT_STARTED,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig
from .const import DOMAIN
from .api import RecalboxAPI
from .intent import async_setup_intents # Pour charger les phrases Assist
from .frontend import JSModuleRegistration

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data.get("host")

    # On stocke l'API pour que button.py puisse la récupérer
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": RecalboxAPI(host)
    }

    # On enregistre les phrases Assist (S'assurer que ce n'est fait qu'une fois)
    if "intents_registered" not in hass.data[DOMAIN]:
        await async_setup_intents(hass)
        hass.data[DOMAIN]["intents_registered"] = True

    # On ajoute "button" à la liste des plateformes
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor", "button"])

    return True






async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register frontend modules after HA startup."""
    module_register = JSModuleRegistration(hass)
    await module_register.async_register()


async def async_setup(hass: HomeAssistant, config: dict) -> bool:

    # enregistrement du chemin statique
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            "/recalbox",
            hass.config.path("custom_components/recalbox/frontend"),
            False
        )
    ])


    async def _setup_frontend(_event=None) -> None:
        await async_register_frontend(hass)

    # If HA is already running, register immediately
    if hass.state == CoreState.running:
        await _setup_frontend()
    else:
        # Otherwise, wait for STARTED event
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _setup_frontend)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Suppression de l'intégration."""
    return await hass.config_entries.async_unload_platforms(entry, ["binary_sensor"])


