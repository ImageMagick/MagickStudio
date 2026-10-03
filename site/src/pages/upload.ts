import { studio } from '../studio'
import { busy, help, showStatus } from '../ui'

const exampleImage = 'https://imagemagick.org/image/wizard.jpg'

async function open(action: () => Promise<unknown>) {
    const result = await busy('Reading your image…', action)
    if (result !== undefined)
        location.hash = '#/view'
}

export function renderUpload(container: HTMLElement) {
    container.innerHTML = `
<br>
<p class="lead">To get started, click <span class="fw-bold">Choose File</span> to browse and open an image from your device, or enter the URL of an image hosted online. When you're ready, click <span class="fw-bold">View</span> to proceed and begin editing, converting, or composing your image.</p>
<form id="uploadForm">
  <table class="table table-sm table-hover table-striped">
    <tr>
      <td>${help('Filename', 'Filename')}:</td>
      <td><input class="form-control" type="file" name="File" id="file"></td>
    </tr>
    <tr>
      <td>${help('URL', 'URL')}:</td>
      <td><input class="form-control" type="text" name="URL" id="url" size="50"></td>
    </tr>
  </table><br>
  Press to <input class="btn btn-primary" type="submit" value="view"> your image or <input class="btn btn-warning" type="reset" value="reset"> the form.
</form>
<br> <br>
An example <a href="#/upload" id="example">image</a> is available to help you get familiar with <code>Magick Online Studio</code>, version <span id="version">…</span>.
<br> <br>
<fieldset>
<legend>Browser Version</legend>
<p>This version of <code>Magick Online Studio</code> runs entirely in your browser and does not yet include every tool. To use all of the tools, run the complete studio on your own computer with <a href="#/docker">Docker</a>.</p>
</fieldset>
<br>
<fieldset>
<legend>Privacy Notice</legend>
<p class="text-warning">Your images never leave your device. This version of Magick Online Studio runs ImageMagick directly in your browser using WebAssembly, so all processing happens locally and nothing is uploaded to our servers. When you enter a URL, your browser downloads the image directly from that website. Images are kept in memory only and are discarded when you close or reload the page.</p>
</fieldset>
<br>
<fieldset>
<legend>Liability Notice</legend>
<p class="text-warning">By using this service, you acknowledge and agree that ImageMagick Studio LLC shall not be held liable for any data loss, consequential damages, or privacy-related issues that may arise from your use of the platform.

Use of this service is at your own risk, and it is your responsibility to ensure that any content you open complies with applicable laws.</p>
</fieldset>
<br>`

    const form = container.querySelector('#uploadForm') as HTMLFormElement
    const fileInput = container.querySelector('#file') as HTMLInputElement
    const urlInput = container.querySelector('#url') as HTMLInputElement

    form.addEventListener('submit', event => {
        event.preventDefault()
        const file = fileInput.files?.[0]
        const url = urlInput.value.trim()
        if (file !== undefined)
            void open(async () => studio.load(new Uint8Array(await file.arrayBuffer()), file.name))
        else if (url !== '')
            void open(() => studio.loadFromUrl(url))
        else
            showStatus('Please choose a file or enter the URL of an image.')
    })

    container.querySelector('#example')?.addEventListener('click', event => {
        event.preventDefault()
        void open(() => studio.loadFromUrl(exampleImage))
    })

    studio.initialize()
        .then(result => {
            const version = container.querySelector('#version')
            if (version !== null)
                version.textContent = /ImageMagick (\S+)/.exec(result.version)?.[1] ?? result.version
        })
        .catch(() => undefined)
}
