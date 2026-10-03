export function escapeHtml(value: string): string {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;')
}

export function errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : String(error)
}

const statusElement = () => document.getElementById('status') as HTMLDivElement

export function showStatus(message: string, kind: 'danger' | 'info' = 'danger') {
    const element = statusElement()
    element.className = `alert alert-${kind}`
    element.textContent = message
}

export function clearStatus() {
    const element = statusElement()
    element.className = 'alert d-none'
    element.textContent = ''
}

export function showBusy(message: string) {
    const element = statusElement()
    element.className = 'alert alert-info d-flex align-items-center'
    element.innerHTML = `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span><span>${escapeHtml(message)}</span>`
}

export async function busy<T>(message: string, action: () => Promise<T>): Promise<T | undefined> {
    showBusy(message)
    try {
        const result = await action()
        clearStatus()
        return result
    } catch (error) {
        showStatus(errorMessage(error))
        return undefined
    }
}

export function help(page: string, label: string): string {
    return `<a href="${page}.html" target="help">${escapeHtml(label)}</a>`
}
