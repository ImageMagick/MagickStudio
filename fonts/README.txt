You need to specify which fonts MagickStudio can use.  Under Linux, use
this command:

  cd MagickStudio/fonts
  cp *.ttf /usr/local/share/fonts
  fc-cache -fv
