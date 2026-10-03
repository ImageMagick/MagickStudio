import { escapeHtml } from '../ui'

export function renderUnavailable(container: HTMLElement, tool: string) {
    container.innerHTML = `
<br>
<p class="lead">The <span class="fw-bold">${escapeHtml(tool)}</span> tool is not currently available in this browser version of <code>Magick Online Studio</code>.</p>
<p>You can still use every tool by running the full studio on your own computer with <a href="#/docker">Docker</a>.</p>
<br> <br>`
}
