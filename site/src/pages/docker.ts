export function renderDocker(container: HTMLElement) {
    container.innerHTML = `
<br>
<p class="lead">Run the complete <code>Magick Online Studio</code>, including every tool, on your own computer with <a href="https://www.docker.com/">Docker</a>.</p>
<fieldset>
<legend>Build and run</legend>
<p>Clone the repository and build the image from its root folder:</p>
<pre class="overflow-auto p-3 mb-2 text-body-secondary bg-body-tertiary"><samp>git clone https://github.com/ImageMagick/MagickStudio.git
cd MagickStudio
docker build -t magickstudio .
docker run --rm -p 7377:7377 magickstudio</samp></pre>
<p>Then point your browser to <a href="http://localhost:7377/">http://localhost:7377/</a>.</p>
</fieldset>
<br>
<fieldset>
<legend>Build options</legend>
<p>The image builds ImageMagick and PerlMagick from source. Use the <code>IMAGEMAGICK_VERSION</code> build argument to select another ImageMagick release:</p>
<pre class="overflow-auto p-3 mb-2 text-body-secondary bg-body-tertiary"><samp>docker build --build-arg IMAGEMAGICK_VERSION=7.1.2-32 -t magickstudio .</samp></pre>
<p>If downloading the Debian packages fails, select a different Debian mirror with the <code>DEBIAN_MIRROR</code> build argument:</p>
<pre class="overflow-auto p-3 mb-2 text-body-secondary bg-body-tertiary"><samp>docker build --build-arg DEBIAN_MIRROR=ftp.nl.debian.org -t magickstudio .</samp></pre>
</fieldset>
<br> <br>`
}
