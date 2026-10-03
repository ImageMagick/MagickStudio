import MagickWorker from './magick.worker?worker'

import type { DownloadResult, ImageView, InitializeResult, PaintOptions, WorkerRequest, WorkerResponse } from './messages'

type Request = WorkerRequest extends infer T ? T extends { id: number } ? Omit<T, 'id'> : never : never

export interface CurrentImage {
    url: string
    width: number
    height: number
    title: string
}

const worker = new MagickWorker()
const pending = new Map<number, { resolve: (value: unknown) => void, reject: (reason: Error) => void }>()
let nextId = 1

worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
    const response = event.data
    const callbacks = pending.get(response.id)
    if (callbacks === undefined)
        return
    pending.delete(response.id)
    if (response.ok)
        callbacks.resolve(response.result)
    else
        callbacks.reject(new Error(response.error))
}

function send<T>(request: Request, transfer: Transferable[] = []): Promise<T> {
    const id = nextId++
    return new Promise<T>((resolve, reject) => {
        pending.set(id, { resolve: resolve as (value: unknown) => void, reject })
        worker.postMessage({ ...request, id }, transfer)
    })
}

let initialized: Promise<InitializeResult> | undefined
let current: CurrentImage | undefined

function setCurrent(view: ImageView): CurrentImage {
    if (current !== undefined)
        URL.revokeObjectURL(current.url)
    current = {
        url: URL.createObjectURL(new Blob([view.data as BlobPart], { type: view.mimeType })),
        width: view.width,
        height: view.height,
        title: view.title,
    }
    document.title = view.title
    return current
}

export const studio = {
    initialize(): Promise<InitializeResult> {
        initialized ??= send<InitializeResult>({ type: 'initialize' })
        return initialized
    },

    get current(): CurrentImage | undefined {
        return current
    },

    async load(data: Uint8Array, name: string): Promise<CurrentImage> {
        await this.initialize()
        return setCurrent(await send<ImageView>({ type: 'load', data, name }, [data.buffer]))
    },

    async loadFromUrl(url: string): Promise<CurrentImage> {
        if (!URL.canParse(url) || !/^https?:$/.test(new URL(url).protocol))
            throw new Error(`Invalid URL: ${url}`)
        let response: Response
        try {
            response = await fetch(url, { mode: 'cors' })
        } catch {
            throw new Error(`Unable to download ${url}. The server does not allow this website to read the image (CORS). Please download the image to your device and choose it with the Filename option instead.`)
        }
        if (!response.ok)
            throw new Error(`Unable to download ${url}: ${response.status} ${response.statusText}`)
        const data = new Uint8Array(await response.arrayBuffer())
        const name = new URL(response.url || url).pathname.split('/').pop() || 'image'
        return this.load(data, name)
    },

    pixel(x: number, y: number): Promise<string> {
        return send<string>({ type: 'pixel', x, y })
    },

    async paint(options: PaintOptions): Promise<CurrentImage> {
        return setCurrent(await send<ImageView>({ type: 'paint', options }))
    },

    async download(): Promise<void> {
        const result = await send<DownloadResult>({ type: 'download' })
        const url = URL.createObjectURL(new Blob([result.data as BlobPart], { type: result.mimeType }))
        const link = document.createElement('a')
        link.href = url
        link.download = result.fileName
        document.body.appendChild(link)
        link.click()
        link.remove()
        setTimeout(() => URL.revokeObjectURL(url), 1000)
    },
}
