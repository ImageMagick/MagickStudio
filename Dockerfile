# syntax=docker/dockerfile:1

FROM debian:trixie-slim

ARG IMAGEMAGICK_VERSION=7.1.2-32
# Optional Debian mirror host, for example ftp.nl.debian.org.
ARG DEBIAN_MIRROR=

# 7377 is the decimal ASCII values of "IM" (73 77).
ENV STUDIO_PORT=7377
ENV DOCUMENT_ROOT=/var/www/html/ImageMagick
ENV STUDIO_ROOT=/var/www/html/ImageMagick/MagickStudio

RUN set -eux; \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries; \
    if [ -n "${DEBIAN_MIRROR}" ]; then \
        sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list.d/debian.sources; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apache2 \
        ca-certificates \
        fonts-dejavu-core \
        fonts-liberation \
        fontconfig \
        ghostscript \
        libapache2-mod-php \
        libcgi-pm-perl \
        libdigest-sha3-perl \
        libwww-perl \
        perl; \
    savedAptMark="$(apt-mark showmanual)"; \
    apt-get install -y --no-install-recommends \
        curl \
        g++ \
        libbz2-dev \
        libdjvulibre-dev \
        libfftw3-dev \
        libfontconfig-dev \
        libfreetype-dev \
        libheif-dev \
        libjpeg-dev \
        libjxl-dev \
        liblcms2-dev \
        liblqr-1-0-dev \
        liblzma-dev \
        libopenexr-dev \
        libopenjp2-7-dev \
        libperl-dev \
        libpng-dev \
        libraw-dev \
        librsvg2-dev \
        libtiff-dev \
        libwebp-dev \
        libxml2-dev \
        libzip-dev \
        libzstd-dev \
        make \
        pkg-config \
        zlib1g-dev; \
    mkdir /tmp/imagemagick; \
    curl -fsSL "https://github.com/ImageMagick/ImageMagick/archive/refs/tags/${IMAGEMAGICK_VERSION}.tar.gz" \
        | tar -xz --strip-components=1 -C /tmp/imagemagick; \
    cd /tmp/imagemagick; \
    ./configure \
        --disable-docs \
        --disable-static \
        --with-perl \
        --without-x; \
    make -j"$(nproc)"; \
    make install; \
    ldconfig; \
    cd /; \
    rm -rf /tmp/imagemagick; \
    # Keep only the runtime libraries required by ImageMagick and PerlMagick.
    apt-mark auto '.*' > /dev/null; \
    apt-mark manual $savedAptMark > /dev/null; \
    find /usr/local -type f \( -name '*.so*' -o -perm -u+x \) -exec ldd '{}' ';' 2>/dev/null \
        | awk '/=>/ { print $(NF-1) }' \
        | sort -u \
        | xargs -r realpath \
        | xargs -r dpkg-query --search 2>/dev/null \
        | cut -d: -f1 \
        | sort -u \
        | xargs -r apt-mark manual; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    rm -rf /var/lib/apt/lists/*; \
    magick -version; \
    perl -MImage::Magick -e 'print "PerlMagick $Image::Magick::VERSION\n"'

COPY app/ ${STUDIO_ROOT}/

RUN set -eux; \
    find "${STUDIO_ROOT}" -type f \( -name '*.cgi' -o -name '*.pm' -o -name '*.pl' \) -exec sed -i 's/\r$//' '{}' +; \
    chmod 755 "${STUDIO_ROOT}"/scripts/*.cgi; \
    for dir in clipboard comments session_info tmp workarea; do \
        chown www-data:www-data "${STUDIO_ROOT}/${dir}"; \
        chmod 775 "${STUDIO_ROOT}/${dir}"; \
    done; \
    a2dismod -f autoindex; \
    fc-cache -f; \
    chown www-data:www-data /var/cache/fontconfig; \
    a2enmod cgi; \
    printf 'Listen %s\n' "${STUDIO_PORT}" > /etc/apache2/ports.conf; \
    printf 'ServerName localhost\n' > /etc/apache2/conf-available/servername.conf; \
    a2enconf servername; \
    ln -sfT /dev/stdout /var/log/apache2/access.log; \
    ln -sfT /dev/stderr /var/log/apache2/error.log

COPY <<'EOF' /etc/apache2/sites-available/000-default.conf
<VirtualHost *:${STUDIO_PORT}>
    DocumentRoot ${DOCUMENT_ROOT}

    RedirectMatch ^/(MagickStudio/?)?$ /MagickStudio/scripts/MagickStudio.cgi

    <Directory ${STUDIO_ROOT}>
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>

    <Directory ${STUDIO_ROOT}/scripts>
        Options +ExecCGI
        AddHandler cgi-script .cgi
    </Directory>

    <FilesMatch "\.(pm|pl)$">
        Require all denied
    </FilesMatch>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF

RUN printf 'export STUDIO_PORT=%s\nexport DOCUMENT_ROOT=%s\nexport STUDIO_ROOT=%s\n' "${STUDIO_PORT}" "${DOCUMENT_ROOT}" "${STUDIO_ROOT}" >> /etc/apache2/envvars

EXPOSE 7377

CMD ["apache2ctl", "-D", "FOREGROUND"]
