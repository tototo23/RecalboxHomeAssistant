# button.py
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    # Fonction pour forcer le statut à OFF dans HA si l'appel au WS a bien eu un retour 200
    async def force_off(result):
        if result :
            # On cherche l'entité binary_sensor dans le registre d'états
            # Note: Adaptez le nom si votre entité ne suit pas ce pattern exact
            entity_id = f"binary_sensor.recalbox_{entry.data.get('host').replace('.', '_')}"
            state = hass.states.get(entity_id)
            if state:
                await asyncio.sleep(15)
                # On force l'état à 'off' manuellement
                hass.states.async_set(entity_id, "off", state.attributes)

    async_add_entities([
        RecalboxAPIButton(api, "Shutdown", "/api/system/shutdown", "mdi:power", entry, 80, callback=force_off),
        RecalboxAPIButton(api, "Reboot", "/api/system/reboot", "mdi:restart", entry, 80),
        RecalboxScreenshotButton(api, entry)
    ])

class RecalboxAPIButton(ButtonEntity):
    def __init__(self, api, name, path, icon, entry, port=80, callback=None):
        self._api = api
        self._path = path
        self._port = port
        self._config_entry = entry
        self._attr_name = f"Recalbox {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._name = name
        self._callback = callback

    @property
    def device_info(self):
        """Lien vers l'appareil parent."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    async def async_press(self):
        # On envoie l'ordre API
        result = await self._api.post_api(self._path, self._port)
        # Si un callback est défini (pour Shutdown), on l'exécute
        if self._callback:
            await self._callback(result)


class RecalboxScreenshotButton(ButtonEntity):
    def __init__(self, api, entry):
        self._api = api
        self._attr_name = "Recalbox Screenshot"
        self._attr_unique_id = f"{entry.entry_id}_screenshot"
        self._attr_icon = "mdi:camera"
        self._config_entry = entry

    @property
    def device_info(self):
        """Lien vers l'appareil parent."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    async def async_press(self):
        if await self._api.screenshot():
            # 2. Déclenchement du vrai Toast via l'événement frontend
            self.hass.bus.async_fire("connection_status_updated", {
                "message": "La capture d'écran a été faite, et stockée dans le dossier screenshots de Recalbox !",
            })

            # MÉTHODE DE SECOURS (La plus compatible) :
            # On utilise le service interne de notification mais on le supprime presque aussitôt
            # ou on utilise l'appel de service qui génère le toast de succès par défaut.
            self.hass.async_create_task(
                self.hass.services.async_call(
                    "frontend",
                    "set_theme",
                    {"name": "default"}, # Ne change rien si déjà par défaut, mais réveille l'UI
                )
            )



