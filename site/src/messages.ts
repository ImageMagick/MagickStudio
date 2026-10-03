export type PaintType = 'None' | 'Color' | 'Matte'

export interface PaintOptions {
    x: number
    y: number
    fuzz: string
    method: string
    type: PaintType
    fill: string
    border: string
}

export type WorkerRequest =
    | { id: number, type: 'initialize' }
    | { id: number, type: 'load', data: Uint8Array, name: string }
    | { id: number, type: 'pixel', x: number, y: number }
    | { id: number, type: 'paint', options: PaintOptions }
    | { id: number, type: 'download' }

export interface ImageView {
    data: Uint8Array
    mimeType: string
    width: number
    height: number
    title: string
}

export interface InitializeResult {
    version: string
    delegates: string
    paintMethods: string[]
}

export interface DownloadResult {
    data: Uint8Array
    fileName: string
    mimeType: string
}

export type WorkerResponse =
    | { id: number, ok: true, result: unknown }
    | { id: number, ok: false, error: string }
