
INSTALL INSTRUCTIONS

  ImageMagick Studio requires both ImageMagick and PerlMagick.  See

      https://imagemagick.org/

  for details.

  ImageMagick - Online Studio can read and write many of the more popular
  image formats directly from a Web page including JPEG, TIFF, PNM, GIF, and
  Photo CD.  In addition you can interactively resize, rotate, sharpen,
  color reduce, or add special effects to an image and save your
  completed work in the same or differing image format.

  To get the ImageMagick Studio image engine working on your system, edit
  scripts/MagickStudio.pm and set
  
      $DocumentRoot='/var/www/html';
      $DocumentDirectory='/MagickStudio';
  
  with the correct path information.  You will also want to review other
  variables and change where appropriate.

  MagickStudio requires ImageMagick 6.4.1 and PerlMagick 5.8 or above.
  These Perl packages CGI.pm (version 2.72 or above), LWP, and MD5 are also
  required.  These are available from CPAN (http://www.perl.com/CPAN/).

  Type

      cd MagickStudio
      scripts/MagickStudio.cgi

  for a basic test to see if the required packages are installed properly.

  Next, modify your web server configuration files to allow
  scripts/MagickStudio.cgi to execute.  On Windows, we use
  scripts/MagickStudio.pl instead since this extension is recognized
  when ActiveState perl is installed.

  Under Windows, copy all IM*dll and *.mgk files to C:\ImageMagick and
  the remaining excutables and DLL's to the directory where perl.exe resides
  (typically C:\Perl\bin).

  The workarea and session_info directory must be writable.  On my
  system, Apache runs as UID apache so I type

      cd MagickStudio
      chgrp -R apache ../MagickStudio

  Next, point your browser to the ImageMagick Studio script.  For example,

      https://mywebsite.org/MagickStudio

  and press the sample image URL.  Report any problems to
  https://github.com/ImageMagick/ImageMagick/discussions.

  Note, the ImageMagick Studio engine creates temporary files in the
  workarea directory.  It automatically deletes them whenever someone
  invokes the engine and they are at least 1 day old.  However, the
  workarea can require alot of disk space depending on the image sizes
  and how often the engine is invoked.

  Add your own TrueType fonts to the MagickStudio/fonts directory.  The
  ImageMagick Studio script will automatically recognize them.

  Thanks to http://www.pixelsight.com/ for many of the Web page icons.


COPYRIGHT

  Copyright 1999-2021 ImageMagick Studio LLC, a non-profit organization
  dedicated to making software imaging solutions freely available.

  You may not use this file except in compliance with the License.  You may
  obtain a copy of the License at

    https://imagemagick.org/license/

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
