import { cpSync, existsSync, readdirSync, statSync, createReadStream } from 'node:fs'
import { extname, join, resolve, sep } from 'node:path'
import { fileURLToPath, URL } from 'node:url'

import { defineConfig, type Plugin } from 'vite'

const appRoot = fileURLToPath(new URL('../app', import.meta.url))
const sharedFolders = ['images', 'style']

const mimeTypes: Record<string, string> = {
    '.css': 'text/css',
    '.gif': 'image/gif',
    '.html': 'text/html',
    '.ico': 'image/x-icon',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
}

function helpPages(): string[] {
    return readdirSync(appRoot).filter(name => name.endsWith('.html'))
}

// Shares the help pages, stylesheets and images of the CGI version in ../app instead of duplicating them.
function shareAppFiles(): Plugin {
    let outDir = 'dist'
    return {
        name: 'share-app-files',
        configResolved(config) {
            outDir = resolve(config.root, config.build.outDir)
        },
        configureServer(server) {
            const base = server.config.base
            server.middlewares.use((req, res, next) => {
                const url = decodeURIComponent((req.url ?? '').split('?')[0])
                if (!url.startsWith(base))
                    return next()
                const relative = url.substring(base.length)
                const isShared = sharedFolders.some(folder => relative.startsWith(`${folder}/`)) || helpPages().includes(relative)
                const file = resolve(appRoot, relative)
                if (!isShared || !file.startsWith(appRoot + sep) || !existsSync(file) || !statSync(file).isFile())
                    return next()
                res.setHeader('Content-Type', mimeTypes[extname(file).toLowerCase()] ?? 'application/octet-stream')
                createReadStream(file).pipe(res)
            })
        },
        closeBundle() {
            for (const folder of sharedFolders)
                cpSync(join(appRoot, folder), join(outDir, folder), { recursive: true, filter: source => !source.endsWith('Makefile') })
            for (const page of helpPages())
                cpSync(join(appRoot, page), join(outDir, page))
        },
    }
}

export default defineConfig({
    base: '/',
    plugins: [
        shareAppFiles(),
    ],
    server: {
        fs: {
            allow: ['..'],
        },
    },
    optimizeDeps: {
        exclude: ['@imagemagick/magick-wasm'],
    },
    worker: {
        format: 'es',
    },
    build: {
        target: 'es2022',
    },
})
