import { studio } from '../studio'
import { escapeHtml } from '../ui'

export async function renderIdentify(container: HTMLElement) {
    if (studio.current === undefined) {
        location.replace('#/upload')
        return
    }

    const { fileName, text } = await studio.identify()
    container.innerHTML = `
<p class="lead">Here is a description of your image, <code>${escapeHtml(fileName)}</code>:</p>
<ul><pre class="overflow-auto p-3 mb-2 text-body-secondary bg-body-tertiary" style="max-height:75svh;"><samp>${escapeHtml(text)}</samp></pre></ul>
<br> <br>`
}
