class RecalboxCard extends HTMLElement {
  set hass(hass) {
    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.innerHTML = `<ha-card><div style="padding:16px; color:red;">Entité non trouvée : ${entityId}</div></ha-card>`;
      return;
    }

    // On ne crée la structure de base qu'une seule fois
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="Recalbox">
          <style>
            .card-content { padding: 0 16px 16px 16px; }
            .game-img { width: 100%; border-radius: 8px; margin: 10px 0; }
            .status-on { color: var(--success-color); font-weight: bold; }
            .info-row { display: flex; align-items: center; margin: 8px 0; }
            .info-row ha-icon { margin-right: 12px; color: var(--primary-text-color); }
            .actions { display: flex; justify-content: space-around; padding: 8px; border-top: 1px solid var(--divider-color); }
          </style>
          <div id="container"></div>
        </ha-card>
      `;
      this.content = this.querySelector('#container');
    }

    const game = state.attributes.game || "-";
    const consoleName = state.attributes.console || "-";
    const genre = state.attributes.genre || "-";
    const imageUrl = state.attributes.imageUrl || "";
    const isOn = state.state === "on";

    // Construction du contenu dynamique
    let html = `
      <div class="card-content">
        <div class="info-row">
          <ha-icon icon="mdi:controller"></ha-icon>
          <span>Statut: <span class="${isOn ? 'status-on' : ''}">${state.state.toUpperCase()}</span></span>
        </div>
    `;

    if (isOn) {
      html += `
        <div class="info-row"><ha-icon icon="mdi:sony-playstation"></ha-icon><span>Console: ${consoleName}</span></div>
        <div class="info-row"><ha-icon icon="mdi:gamepad-variant-outline"></ha-icon><span>Jeu: ${game}</span></div>
        <div class="info-row"><ha-icon icon="mdi:folder-outline"></ha-icon><span>Genre: ${genre}</span></div>
        ${imageUrl && imageUrl.length > 5 ? `<img class="game-img" src="${imageUrl}">` : ''}

        <div class="actions">
          <ha-icon-button icon="mdi:power" title="Shutdown" id="btn-stop"></ha-icon-button>
          <ha-icon-button icon="mdi:restart" title="Reboot" id="btn-reboot"></ha-icon-button>
          <ha-icon-button icon="mdi:camera" title="Screenshot" id="btn-snap"></ha-icon-button>
        </div>
      `;
    } else {
      html += `<p>La console est éteinte.</p>`;
    }

    html += `</div>`;
    this.content.innerHTML = html;

    // Gestion des clics sécurisée (uniquement si les boutons existent)
    const snapBtn = this.content.querySelector('#btn-snap');
    const rebootBtn = this.content.querySelector('#btn-reboot');
    const stopBtn = this.content.querySelector('#btn-stop');
    if (snapBtn) {
      snapBtn.onclick = () => hass.callService('button', 'press', { entity_id: this.config.screenshot_button });
    }
    if (stopBtn) {
      rebootBtn.onclick = () => hass.callService('button', 'press', { entity_id: this.config.reboot_button });
      stopBtn.onclick = () => hass.callService('button', 'press', { entity_id: this.config.shutdown_button });
    }
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Vous devez définir l'entité binary_sensor");
    this.config = config;
  }

  getCardSize() { return 3; }
}

customElements.define('recalbox-card', RecalboxCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "recalbox-card",
  name: "Recalbox Card",
  preview: true,
  description: "Affiche l'état de la console, du jeu en cours, et des contrôles de base."
});