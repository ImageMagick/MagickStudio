import type { PaintOptions, PaintType } from '../messages'
import { studio, type CurrentImage } from '../studio'
import { busy, escapeHtml, help } from '../ui'

const paintTypes: PaintType[] = ['None', 'Color', 'Matte']

const settings = {
    fuzz: '0%',
    method: 'Point',
    type: 'None' as PaintType,
    fill: 'none',
    border: 'none',
}

function options(values: string[], selected: string): string {
    return values
        .map(value => `<option value="${escapeHtml(value)}"${value === selected ? ' selected' : ''}>${escapeHtml(value)}</option>`)
        .join('')
}

export async function renderView(container: HTMLElement) {
    const image = studio.current
    if (image === undefined) {
        location.replace('#/upload')
        return
    }

    const { paintMethods } = await studio.initialize()
    container.innerHTML = `
<p class="lead">Here is your image.  Click on a tab above to interactively resize, rotate, sharpen, color reduce, or add special effects to your image and save the completed work in the same or differing image format.  For more information, see <a href="https://imagemagick.org/" target="_blank" rel="noopener">ImageMagick</a>.</p>
<p>You can optionally ${help('Paint', 'paint')} on your image.  Set any optional attributes below and click on the appropriate location within your image.</p>
<img class="img-fluid mx-auto d-block border" id="image" alt="${escapeHtml(image.title)}" style="cursor:crosshair"><br>
<ul id="pixel" class="d-none"><pre class="overflow-auto p-3 mb-2 text-body-secondary bg-body-tertiary" style="max-height:75svh;"><samp></samp></pre></ul>
<br>
<fieldset>
<legend>Paint Properties</legend>
<dl><dd>
<table class="table table-sm table-hover table-striped">
<tr>
<th>${help('Fuzz', 'Fuzz')}</th>
<th>${help('Paint', 'Method')}</th>
<th>${help('Paint', 'Paint Type')}</th>
</tr>
<tr>
<td><input class="form-control" type="text" id="fuzz" size="25" value="${escapeHtml(settings.fuzz)}"></td>
<td><select class="form-control" id="method">${options(paintMethods, settings.method)}</select></td>
<td><select class="form-control" id="type">${options(paintTypes, settings.type)}</select></td>
</tr>
</table><br>
<table class="table table-sm table-hover table-striped">
<tr>
<th>${help('Color', 'Fill Color')}</th>
<th>${help('Color', 'Border Color')}</th>
</tr>
<tr>
<td><input class="form-control" type="text" id="fill" size="25" value="${escapeHtml(settings.fill)}"></td>
<td><input class="form-control" type="text" id="border" size="25" value="${escapeHtml(settings.border)}"></td>
</tr>
</table>
</dd></dl>
</fieldset>
<br> <br> <br> <br>`

    const img = container.querySelector('#image') as HTMLImageElement
    const pixel = container.querySelector('#pixel') as HTMLElement
    const field = (id: string) => container.querySelector(`#${id}`) as HTMLInputElement | HTMLSelectElement

    const show = (current: CurrentImage) => {
        img.src = current.url
        img.width = current.width
        img.height = current.height
        img.alt = current.title
    }
    show(image)

    const ids = ['fuzz', 'method', 'type', 'fill', 'border'] as const
    const readSettings = () => {
        for (const id of ids)
            (settings as Record<typeof id, string>)[id] = field(id).value
    }

    let painting = false
    const paintAt = async (x: number, y: number) => {
        if (painting)
            return
        painting = true
        readSettings()
        const paint: PaintOptions = { x, y, ...settings }
        const text = await busy(paint.type === 'None' ? 'Reading pixel…' : 'Painting…', async () => {
            if (paint.type !== 'None')
                show(await studio.paint(paint))
            return studio.pixel(x, y)
        })
        painting = false
        if (text === undefined)
            return
        pixel.classList.remove('d-none')
        const samp = pixel.querySelector('samp')
        if (samp !== null)
            samp.textContent = text
    }

    for (const id of ids)
        field(id).addEventListener('change', readSettings)

    // Like the CGI, pressing Enter in a text field submits the form as a click at 0,0.
    for (const id of ['fuzz', 'fill', 'border'] as const) {
        field(id).addEventListener('keydown', event => {
            if ((event as KeyboardEvent).key !== 'Enter')
                return
            event.preventDefault()
            void paintAt(0, 0)
        })
    }

    img.addEventListener('click', event => {
        const x = Math.floor(event.offsetX * img.naturalWidth / img.clientWidth)
        const y = Math.floor(event.offsetY * img.naturalHeight / img.clientHeight)
        void paintAt(x, y)
    })
}
