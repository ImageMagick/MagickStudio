// Copyright @ 1999 ImageMagick Studio LLC, a non-profit organization
// dedicated to making software imaging solutions freely available.

import type { ResizeAlgorithm, ResizeOptions } from '../messages'
import { studio } from '../studio'
import { busy, escapeHtml, help } from '../ui'

const algorithms: ResizeAlgorithm[] = [
    'resize',
    'adaptive resize',
    'double size',
    'extent',
    'half size',
    'liquid rescale',
    'resample',
    'sample',
    'scale',
    'thumbnail',
]

const filters = [
    'Point', 'Box', 'Triangle', 'Hermite', 'Hann', 'Hamming', 'Blackman',
    'Gaussian', 'Quadratic', 'Cubic', 'Catrom', 'Mitchell', 'Jinc', 'Sinc',
    'SincFast', 'Kaiser', 'Welch', 'Parzen', 'Bohman', 'Bartlett', 'Lagrange',
    'Lanczos', 'LanczosSharp', 'Lanczos2', 'Lanczos2Sharp', 'Robidoux',
    'RobidouxSharp', 'Cosine', 'Spline', 'LanczosRadius', 'CubicSpline',
    'MagicKernelSharp2013', 'MagicKernelSharp2021',
]

const gravities = [
    'Northwest', 'North', 'Northeast', 'West', 'Center',
    'East', 'Southwest', 'South', 'Southeast',
]

const settings = {
    algorithm: 'resize' as ResizeAlgorithm,
    filter: 'Mitchell',
    support: '0.0',
    blur: '1.0',
    gravity: 'Center',
    background: 'none',
}

function options(values: string[], selected: string): string {
    return values
        .map(value => `<option value="${escapeHtml(value)}"${value === selected ? ' selected' : ''}>${escapeHtml(value)}</option>`)
        .join('')
}

export async function renderResize(container: HTMLElement) {
    const image = studio.current
    if (image === undefined) {
        location.replace('#/upload')
        return
    }

    container.innerHTML = `
<p class="lead">To ${help('Resize', 'resize')} your image, specify the desired size and scaling method. Methods marked with an asterisk require a size. Then press <code>resize</code> to continue.</p>
<form id="resizeForm">
<dl>
<dt class="fw-bold mb-2">Image size:</dt>
<dd class="mb-3"><input class="form-control" type="text" id="geometry" value="${image.width}x${image.height}" aria-label="Image size"></dd>
<dt class="fw-bold mb-2">Choose a scaling method:</dt>
<dd class="mb-3"><div class="row">${algorithms.map((algorithm, index) => `
<div class="col-md-4"><div class="form-check">
<input class="form-check-input" type="radio" name="algorithm" id="algorithm${index}" value="${escapeHtml(algorithm)}"${algorithm === settings.algorithm ? ' checked' : ''}>
<label class="form-check-label" for="algorithm${index}">${escapeHtml(algorithm)}${algorithm !== 'double size' && algorithm !== 'half size' ? ' *' : ''}</label>
</div></div>`).join('')}
</div></dd>
</dl>
<fieldset>
<legend>Resize Properties</legend>
<table class="table table-sm table-hover table-striped">
<tr><th>${help('Resize', 'Filter')}</th><th>${help('Resize', 'Support')}</th><th>${help('Resize', 'Blur')}</th></tr>
<tr>
<td><select class="form-select" id="filter">${options(filters, settings.filter)}</select></td>
<td><input class="form-control" type="number" step="any" id="support" value="${settings.support}"></td>
<td><input class="form-control" type="number" step="any" id="blur" value="${settings.blur}"></td>
</tr>
</table>
<table class="table table-sm table-hover table-striped">
<tr><th>${help('Resize', 'Gravity')}</th><th>${help('Color', 'Background Color')}</th></tr>
<tr>
<td><select class="form-select" id="gravity">${options(gravities, settings.gravity)}</select></td>
<td><input class="form-control" type="text" id="background" value="${escapeHtml(settings.background)}"></td>
</tr>
</table>
</fieldset>
<br>
Press to <button class="btn btn-primary" type="submit">resize</button> your image or <button class="btn btn-warning" type="reset">reset</button> the form.
</form>
<br> <br>`

    const form = container.querySelector('#resizeForm') as HTMLFormElement
    const field = (id: string) => container.querySelector(`#${id}`) as HTMLInputElement | HTMLSelectElement
    const readSettings = () => {
        const selected = container.querySelector<HTMLInputElement>('input[name="algorithm"]:checked')
        if (selected === null)
            return undefined
        const algorithm = algorithms.find(value => value === selected.value)
        if (algorithm === undefined)
            return undefined
        return {
            geometry: field('geometry').value,
            algorithm,
            filter: field('filter').value,
            support: field('support').value,
            blur: field('blur').value,
            gravity: field('gravity').value,
            background: field('background').value,
        } satisfies ResizeOptions
    }

    form.addEventListener('submit', event => {
        event.preventDefault()
        const options = readSettings()
        if (options === undefined)
            return
        Object.assign(settings, options)
        void busy('Resizing…', () => studio.resize(options)).then(result => {
            if (result !== undefined)
                location.hash = '#/view'
        })
    })
}
