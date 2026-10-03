import 'bootstrap/dist/css/bootstrap.min.css'
import '../../app/assets/magick-template.css'
import 'bootstrap'

import { renderDocker } from './pages/docker'
import { renderUnavailable } from './pages/unavailable'
import { renderUpload } from './pages/upload'
import { renderView } from './pages/view'
import { studio } from './studio'
import { busy, clearStatus, errorMessage, showStatus } from './ui'

const unavailableTools: Record<string, string> = {
    identify: 'Identify',
    transform: 'Transform',
    resize: 'Resize',
    effects: 'Effects',
    fx: 'F/X',
    enhance: 'Enhance',
    colormap: 'Colormap',
    decorate: 'Decorate',
    annotate: 'Annotate',
    draw: 'Draw',
    composite: 'Composite',
    compare: 'Compare',
}

type Theme = 'light' | 'dark' | 'auto'

const themeIcons: Record<Theme, string> = { light: '☀️', dark: '🌙', auto: '🌓' }

function systemTheme(): 'light' | 'dark' {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function savedTheme(): Theme {
    const theme = localStorage.getItem('theme')
    return theme === 'light' || theme === 'dark' ? theme : 'auto'
}

function setTheme(theme: Theme) {
    localStorage.setItem('theme', theme)
    const icon = document.getElementById('currentThemeIcon')
    if (icon !== null)
        icon.textContent = themeIcons[theme]
    document.documentElement.setAttribute('data-bs-theme', theme === 'auto' ? systemTheme() : theme)
}

function currentRoute(): string {
    const match = /^#\/([a-z]+)/.exec(location.hash)
    return match?.[1] ?? 'upload'
}

function highlightMenu(route: string) {
    document.querySelectorAll<HTMLElement>('[data-tools]').forEach(element => {
        element.classList.toggle('active', (element.dataset.tools ?? '').split(' ').includes(route))
    })
}

async function render() {
    const route = currentRoute()
    const container = document.getElementById('page') as HTMLElement
    clearStatus()
    highlightMenu(route)
    document.title = studio.current?.title ?? 'Magick Online Studio'
    try {
        if (route === 'view')
            await renderView(container)
        else if (route === 'docker')
            renderDocker(container)
        else if (route in unavailableTools)
            renderUnavailable(container, unavailableTools[route])
        else
            renderUpload(container)
    } catch (error) {
        showStatus(errorMessage(error))
    }
    window.scrollTo(0, 0)
}

document.querySelectorAll<HTMLElement>('[data-theme]').forEach(element => {
    element.addEventListener('click', event => {
        event.preventDefault()
        setTheme(element.dataset.theme as Theme)
    })
})
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => setTheme(savedTheme()))
setTheme(savedTheme())

document.getElementById('backToTop')?.addEventListener('click', event => {
    event.preventDefault()
    window.scrollTo(0, 0)
})

document.getElementById('download')?.addEventListener('click', () => {
    if (studio.current === undefined) {
        showStatus('Please upload an image first.')
        return
    }
    void busy('Preparing your download…', () => studio.download())
})

window.addEventListener('hashchange', () => void render())
void render()

studio.initialize().catch(error => {
    showStatus(`Unable to start ImageMagick in your browser: ${errorMessage(error)}. This website requires a browser with support for 64-bit WebAssembly (memory64), such as a recent version of Chrome, Edge or Firefox.`)
})
