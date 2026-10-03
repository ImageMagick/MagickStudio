import wasmUrl from '@imagemagick/magick-wasm/x64/magick.wasm?url'
import {
    CompositeOperator,
    DrawableBorderColor,
    DrawableColor,
    DrawableFillColor,
    initializeImageMagickx64,
    Magick,
    MagickColor,
    MagickFormat,
    MagickImageCollection,
    PaintMethod,
    Percentage,
    Quantum,
    type IMagickImage,
    type IMagickImageCollection,
} from '@imagemagick/magick-wasm'

import type { DownloadResult, ImageView, InitializeResult, PaintOptions, WorkerRequest, WorkerResponse } from './messages'

interface StudioImage {
    images: IMagickImageCollection
    name: string
    format: MagickFormat
}

let current: StudioImage | undefined

const paintMethods = Object.keys(PaintMethod).filter(name => name !== 'Undefined') as (keyof typeof PaintMethod)[]

function requireImage(): StudioImage {
    if (current === undefined)
        throw new Error('Please upload an image first.')
    return current
}

function baseName(fileName: string): string {
    const name = fileName.split(/[\\/]/).pop() ?? fileName
    const dot = name.lastIndexOf('.')
    return dot > 0 ? name.substring(0, dot) : name
}

function formatInfo(format: MagickFormat) {
    return Magick.supportedFormats.find(info => info.format === format)
}

async function initialize(): Promise<InitializeResult> {
    await initializeImageMagickx64(new URL(wasmUrl, self.location.href))
    return {
        version: Magick.imageMagickVersion,
        delegates: Magick.delegates,
        paintMethods,
    }
}

function load(data: Uint8Array, fileName: string): ImageView {
    const images = MagickImageCollection.create()
    try {
        images.read(data)
        if (images.length === 0)
            throw new Error('Unable to read image.')
    } catch (error) {
        images.dispose()
        throw error
    }

    current?.images.dispose()
    current = {
        images,
        name: baseName(fileName) || 'image',
        format: images[0].format,
    }
    return view()
}

function view(): ImageView {
    const { images, name, format } = requireImage()
    const title = `${name}.${format.toLowerCase()}  ${images[0].width}x${images[0].height}`
    return images.clone(coalesced => {
        coalesced.coalesce()
        const animated = coalesced.length > 1
        const outputFormat = animated ? MagickFormat.Gif : MagickFormat.Png
        const width = coalesced[0].width
        const height = coalesced[0].height
        const data = animated
            ? coalesced.write(outputFormat, bytes => bytes.slice())
            : coalesced[0].write(outputFormat, bytes => bytes.slice())
        return {
            data,
            mimeType: animated ? 'image/gif' : 'image/png',
            width,
            height,
            title,
        }
    })
}

function pixel(x: number, y: number): string {
    const { images } = requireImage()
    return images.clone(coalesced => {
        coalesced.coalesce()
        const image = coalesced[0]
        if (x < 0 || y < 0 || x >= image.width || y >= image.height)
            throw new Error('The selected position is outside of the image.')
        const name = image.formatExpression(`%[pixel:p{${x},${y}}]`) ?? ''
        const hex = image.formatExpression(`%[hex:p{${x},${y}}]`) ?? ''
        return `${x},${y}: ${name}  #${hex}`
    })
}

function parseFuzz(value: string): Percentage | undefined {
    const text = value.trim()
    if (text === '')
        return undefined
    const amount = parseFloat(text)
    if (isNaN(amount) || amount < 0)
        throw new Error(`Invalid fuzz value: ${value}`)
    return text.endsWith('%') ? new Percentage(amount) : new Percentage(100 * amount / Quantum.max)
}

function parseColor(value: string): MagickColor {
    return new MagickColor(value.trim() === '' ? 'none' : value.trim())
}

function paintImage(image: IMagickImage, options: PaintOptions, fuzz: Percentage | undefined, method: PaintMethod) {
    const x = options.x - image.page.x
    const y = options.y - image.page.y
    if (fuzz !== undefined)
        image.colorFuzz = fuzz
    const border = new DrawableBorderColor(parseColor(options.border))
    if (options.type === 'Color') {
        image.draw(new DrawableFillColor(parseColor(options.fill)), border, new DrawableColor(x, y, method))
        return
    }

    // Matte only changes the alpha channel, so the region is painted transparent on a copy first.
    image.hasAlpha = true
    image.clone(mask => {
        mask.draw(new DrawableFillColor(new MagickColor('none')), border, new DrawableColor(x, y, method))
        image.composite(mask, CompositeOperator.CopyAlpha)
    })
}

function paint(options: PaintOptions): ImageView {
    const { images } = requireImage()
    if (options.type !== 'None') {
        const method = PaintMethod[options.method as keyof typeof PaintMethod]
        if (method === undefined || method === PaintMethod.Undefined)
            throw new Error(`Invalid paint method: ${options.method}`)
        const fuzz = parseFuzz(options.fuzz)
        for (const image of images)
            paintImage(image, options, fuzz, method)
    }
    return view()
}

function download(): DownloadResult {
    const { images, name, format } = requireImage()
    const info = formatInfo(format)
    const outputFormat = info?.supportsWriting ? format : MagickFormat.Png
    const outputInfo = outputFormat === format ? info : formatInfo(outputFormat)
    const data = images.length > 1 && outputInfo?.supportsMultipleFrames
        ? images.write(outputFormat, bytes => bytes.slice())
        : images[0].write(outputFormat, bytes => bytes.slice())
    return {
        data,
        fileName: `${name}.${outputFormat.toLowerCase()}`,
        mimeType: outputInfo?.mimeType ?? 'application/octet-stream',
    }
}

async function handle(request: WorkerRequest): Promise<unknown> {
    switch (request.type) {
        case 'initialize':
            return initialize()
        case 'load':
            return load(request.data, request.name)
        case 'pixel':
            return pixel(request.x, request.y)
        case 'paint':
            return paint(request.options)
        case 'download':
            return download()
    }
}

function errorMessage(error: unknown): string {
    if (error instanceof Error)
        return error.message
    return String(error)
}

self.onmessage = async (event: MessageEvent<WorkerRequest>) => {
    const { id } = event.data
    let response: WorkerResponse
    try {
        response = { id, ok: true, result: await handle(event.data) }
    } catch (error) {
        response = { id, ok: false, error: errorMessage(error) }
    }

    const result = response.ok ? response.result as { data?: Uint8Array } | undefined : undefined
    const transfer = result?.data instanceof Uint8Array ? [result.data.buffer] : []
    self.postMessage(response, { transfer })
}
