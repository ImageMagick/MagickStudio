#!/usr/bin/perl
#
###############################################################################
#                                                                             #
#                                                                             #
#                                                                             #
#                 M   M   AAA    GGGG  IIIII   CCCC  K   K                    #
#                 MM MM  A   A  G        I    C      K  K                     #
#                 M M M  AAAAA  G GG     I    C      KKK                      #
#                 M   M  A   A  G   G    I    C      K  K                     #
#                 M   M  A   A   GGG   IIIII   CCCC  K   K                    #
#                                                                             #
#                 SSSSS  TTTTT  U   U  DDDD   IIIII   OOO                     #
#                 SS       T    U   U  D   D    I    O   O                    #
#                  SSS     T    U   U  D   D    I    O   O                    #
#                    SS    T    U   U  D   D    I    O   O                    #
#                 SSSSS    T     UUU   DDDD   IIIII   OOO                     #
#                                                                             #
#                                                                             #
#                Image Convert, Edit, and Compose on the Web                  #
#                                                                             #
#                                                                             #
#                           Software Design                                   #
#                             John Cristy                                     #
#                            November 1997                                    #
#                                                                             #
#                                                                             #
#  Copyright (C) 1999-2020 ImageMagick Studio LLC, a non-profit organization  #
#  dedicated to making software imaging solutions freely available.           #
#                                                                             #
#  You may not use this file except in compliance with the License.  You may  #
#  obtain a copy of the License at                                            #
#                                                                             #
#    https://imagemagick.org/script/license.php                               #
#                                                                             #
#  Unless required by applicable law or agreed to in writing, software        #
#  distributed under the License is distributed on an "AS IS" BASIS,          #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
#  See the License for the specific language governing permissions and        #
#  limitations under the License.                                             #
#                                                                             #
###############################################################################
#
#  Magick Studio is a Web interface to PerlMagick that can read and write
#  many of the more popular image formats including JPEG, TIFF, PNM, GIF, and
#  Photo CD.  In addition you can interactively resize, rotate, sharpen, color
#  reduce, or add special effects to your image and save the completed work in
#  the same or differing image format.
#
#

BEGIN {
  use File::Basename;
  $dir=dirname($0);
  chdir $dir or die "Can't chdir to $dir: $!\n";
  # safe now
  push @INC, '.';
}

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use Sys::Hostname;
use MagickStudio;
use strict;

#
# Global variable declarations.
#
my($action, %Functions, $header, $length, $prefix, $q, %seen, $timer,
   $user_agent);

our($ContactInfo, $Debug, $DefaultFont, $DocumentDirectory, $DocumentRoot,
    $ExampleImage, $ExpireCache, $ExpireThreshold, $HashDigestSalt, $IconSize,
    $LoadAverageThreshold, $MaxFilesize, $MaxImageArea, $MaxImageExtent,
    $MaxWorkFiles, $MinExpireAge, $RedirectURL, $SponsorIcon, $SponsorURL,
    $Timeout);

#
# Change these variables to reflect your environment.
#
#$ENV{'ftp_proxy'}='http://webproxy.imagemagick.org/';
#$ENV{'http_proxy'}='http://webproxy.imagemagick.org/';
$ENV{DISPLAY}="$ENV{REMOTE_HOST}:0" if $ENV{REMOTE_HOST};
$ENV{LD_LIBRARY_PATH}='/usr/lib:/usr/openwin/lib:/usr/local/lib';
$ENV{MAGICK_FONT_PATH}=$DocumentRoot . $DocumentDirectory . "/fonts";
$ENV{MAGICK_PRECISION}=15;
$ENV{PATH}='/bin:/usr/bin:/usr/openwin/bin:/usr/local/bin';
$ENV{TMPDIR}=$DocumentRoot . $DocumentDirectory . "/tmp";

#
# Annotate image.
#
sub Annotate
{
  use Image::Magick;

  no strict 'refs';

  my($antialias, $density, $direction, $fill, $font, $geometry, $gravity,
    $image, $kerning, $interline_spacing, $interword_spacing, $path,
    $pointsize, $rotate, $scale, $skew_x, $skew_y, $status, $stroke,
    $strokewidth, $text, $translate, $undercolor);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Annotate image.
  #
  $antialias='false';
  $antialias='true' if $q->param('Antialias') eq 'on';
  $density='90';
  $density=$q->param('Density') if $q->param('Density');
  $direction=$q->param('Direction');
  $fill='none';
  $fill=$q->param('Fill') if $q->param('Fill');
  getstore(Untaint($q->param('FontURL')),'MagickStudio.ttf')
    unless $q->param('FontURL') eq 'http://';
  $font="\@MagickStudio.ttf" if -e 'MagickStudio.ttf';
  $font=($image->QueryFont($q->param('Font')))[10] unless -e 'MagickStudio.ttf';
  $geometry='+0+0';
  $geometry=$q->param('Geometry') if $q->param('Geometry');
  $gravity=$q->param('Gravity');
  $pointsize=int($q->param('Pointsize'));
  $kerning=0.0;
  $kerning=$q->param('Kerning') if $q->param('Kerning');
  $interline_spacing=0.0;
  $interline_spacing=$q->param('InterlineSpacing') if
    $q->param('InterlineSpacing');
  $interword_spacing=0.0;
  $interword_spacing=$q->param('InterwordSpacing') if
    $q->param('InterwordSpacing');
  $rotate=0.0;
  $rotate=$q->param('Rotate') if $q->param('Rotate');
  $scale='0.0, 0.0';
  $scale=$q->param('Scale') if $q->param('Scale');
  $stroke='none';
  $stroke=$q->param('Stroke') if $q->param('Stroke');
  $skew_x=0.0;
  $skew_x=$q->param('SkewX') if $q->param('SkewX');
  $skew_y=0.0;
  $skew_y=$q->param('SkewY') if $q->param('SkewY');
  $strokewidth=1;
  $strokewidth=$q->param('StrokeWidth') if $q->param('StrokeWidth');
  $text=$q->param('Text');
  $translate='0.0, 0.0';
  $translate=$q->param('Translate') if $q->param('Translate');
  $undercolor='none';
  $undercolor=$q->param('Undercolor') if $q->param('Undercolor');
  if ($q->param('Polaroid') eq 'on')
    {
      $image->Polaroid(caption=>$text,font=>$font,fill=>$fill,stroke=>$stroke,
        strokewidth=>$strokewidth,pointsize=>$pointsize,angle=>$rotate,
        gravity=>$gravity,background=>$q->param('BackgroundColor'));
    }
  else
    {
      $image->Annotate(text=>$text,geometry=>$geometry,font=>$font,fill=>$fill,
        stroke=>$stroke,strokewidth=>$strokewidth,undercolor=>$undercolor,
        pointsize=>$pointsize,density=>$density,gravity=>$gravity,
        kerning=>$kerning,'interline-spacing'=>$interline_spacing,
        'interword-spacing'=>$interword_spacing,translate=>$translate,
        scale=>$scale,rotate=>$rotate,skewX=>$skew_x,skewY=>$skew_y,
        antialias=>$antialias,direction=>$direction);
    }
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Annotate image form.
#
sub AnnotateForm
{
  my(@fonts, $image);

  #
  # Display annotate form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Annotate.html" target="help">annotate</a> your image with text, enter your text and location below and press <code>annotate</code>.  There are additional optional attributes below.  Set them as appropriate.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dt>Text:</dt>\n";
  print '<dd>', $q->textarea(-class=>'form-control',-name=>'Text',-columns=>50,
    -rows=>3), "</dd><br />\n";
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Offset</th>\n";
  print "<th>Gravity</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Geometry',
    -size=>25,-value=>'+0+0'), "</td>\n";
  my @types=Image::Magick->QueryOption('gravity');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Gravity',
    -values=>[@types],-default=>'SouthEast'), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'annotate'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Annotate Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Fill Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Stroke Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Undercolor</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Fill',
    -value=>'white',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Stroke',
    -value=>'none',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Undercolor',
    -value=>'none',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>PointSize</th>\n";
  print "<th>Density</th>\n";
  print "<th>Stroke Width</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Pointsize',
    -value=>'24',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Density',
    -value=>'90',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'StrokeWidth',
    -value=>'0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Kerning</th>\n";
  print "<th>Interline Spacing</th>\n";
  print "<th>Interword Spacing</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Kerning',
    -value=>'0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'InterlineSpacing',
    -value=>'0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'InterwordSpacing',
    -value=>'0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/fonts/\">Font</a></th>\n";
  print "<th>Direction</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  $image=new Image::Magick;
  @fonts=$image->QueryFont();
  print '<td>', $q->scrolling_list(-class=>'form-control',-name=>'Font',
    -values=>[@fonts],-size=>10), "</td><br />\n";
  my @types=Image::Magick->QueryOption('direction');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Direction',
    -values=>[@types]), "</td>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'FontURL',
    -value=>'http://',-size=>25), "</td><br />\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Translate</th>\n";
  print "<th>Scale</th>\n";
  print "<th>Rotate</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Translate',
    -value=>'0.0, 0.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Scale',
    -value=>'1.0, 1.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Rotate',
    -value=>'0.0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Skew X</th>\n";
  print "<th>Skew Y</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SkewX',
    -value=>'0.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SkewY',
    -value=>'0.0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Background Color</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BackgroundColor',
    -value=>'none', -size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dt>Miscellaneous options:</dt>\n";
  print '<dd>', $q->checkbox(-name=>'Antialias',
    -label=>' antialias text.',-checked=>'true'), "</dd>\n";
  print '<dd>', $q->checkbox(-name=>'Polaroid',
    -label=>' simulate a Polaroid picture.'), "</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# Suspend service during restricted hours.
#
sub CheckStudioHours
{
  my($hour, $url);

  $hour=(localtime)[2];
  return unless ($hour >= 18) && ($hour < 23);
  $url=$q->self_url . "&Action=" . $action;
  Header("Please Stand By...",-refresh=>"600; URL=$url");
  print <<XXX;
<code>ImageMagick Studio</code> has restricted access from 6PM until 11PM EST.
We have temporarily <i>suspended</i> the processing of your image.
Shortly after 11PM, processing <var>automagically</var> continues and your image is
returned.
XXX
  ;
  Trailer(undef);
}

#
# Suspend service if Studio is too busy.
#
sub CheckStudioStatus
{
  my($load_average, $refresh_rate, $url);

  $load_average=GetLoadAverage();
  return unless $load_average > 2*$LoadAverageThreshold;
  $refresh_rate=int($load_average);
  $url=$q->self_url . "&Action=" . $action;
  Header("Please Stand By...",-refresh=>"$refresh_rate; URL=$url",
    -status=>'502 Service Temporarily Overloaded');
  print <<XXX;
<code>ImageMagick Studio</code> is busy serving other requests.  We have temporarily
<i>suspended</i> the processing of your image.  The current studio status is:
<br />
<center>
<table class=\"table table-condensed table-striped\">
<tr>
  <th>Load Average</th>
  <th>Threshold</th>
</tr>

<tr>
  <td align=center>$load_average</td>
  <td align=center>$LoadAverageThreshold</td>
</tr>
</table>
</center>
<br />
When the studio load average becomes less than the threshold, processing
<var>automagically</var> continues and your image is returned.  The studio status will
be refreshed in $refresh_rate seconds.
XXX
  ;
  Trailer(undef);
}

#
# Choose a MagickStudio tool.
#
sub ChooseTool
{
  my ($function, $tooltype, %Tools);

  %Tools=
  (
    'Upload'=>\&Upload,
    'Download'=>\&Download,
    'View'=>\&View,
    'Identify'=>\&Identify,
    'Colormap'=>\&Colormap,
    'Resize'=>\&Resize,
    'Transform'=>\&Transform,
    'Enhance'=>\&Enhance,
    'Effects'=>\&Effects,
    'FX'=>\&Effects,
    'Decorate'=>\&Decorate,
    'Annotate'=>\&Annotate,
    'Draw'=>\&Draw,
    'Composite'=>\&Composite,
    'Compare'=>\&Compare,
    'Comment'=>\&Comment
  );

  $tooltype=$q->param('ToolType');
  View() unless defined($tooltype);
  Error('Unable to mogrify image','path is not defined')
    unless $q->param('Path');
  SaveQueryState($q->param('SessionID'),$tooltype);
  $function=$Tools{$tooltype};
  &$function() if defined($function);
  Error('Request failed due to malformed query');
}

#
# Colormap image.
#
sub Colormap
{
  use Image::Magick;

  my($colors, $colorspace, $dither, $global_colormap, $image, $levels,
    $measure_error, %options, $parameter, $path, $status, $transparent_color);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Quantize image.
  #
  grep($options{$_}++,$q->param('Options'));
  $colors=$q->param('Parameter');
  $dither='false';
  $dither='true' if $options{'dither'};
  $global_colormap='false';
  $global_colormap='true' if $options{'global colormap'};
  $colorspace='sRGB';
  $colorspace='Gray' if $options{'gray'};
  $colorspace=$q->param('Colorspace') if $q->param('Colorspace');
  $measure_error='False';
  $measure_error='True' if $options{'measure error'};
  $parameter=$q->param('Parameter');
  $transparent_color='none';
  $transparent_color=$q->param('TransparentColor') if
    $q->param('TransparentColor');
  if ($options{'black & white'})
    {
      $colors='2';
      $colorspace='Gray';
    }
  $colorspace='Transparent' if $options{'preserve transparent pixels'};
  if ($options{'map to clipboard'})
    {
      my($colorcube, $filename);

      #
      # Map to the clipboard image.
      #
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $colorcube=Image::Magick->new;
      $status=$colorcube->Read($filename);
      Error($status) if $#$colorcube < 0;
      $image->Remap(image=>$colorcube);
    }
  if ($options{'netscape color cube'})
    {
      my($colorcube);

      #
      # Map to the Netscape colorcube.
      #
      $colorcube=Image::Magick->new;
      $status=$colorcube->Read('netscape:');
      Error($status) if $#$colorcube < 0;
      $image->Remap(image=>$colorcube);
    }
  for ($levels=1; (($levels+1)*($levels+1)*($levels+1)) < $colors; $levels++)
  {
  }
  $image->OrderedDither($parameter) if $options{'ordered dither'};
  $image->Posterize(levels=>$levels,dither=>$dither) if $options{'posterize'};
  $image->Segment(colorspace=>$colorspace) if $options{'segment'};
  $image->Kmeans($parameter) if $options{'kmeans'};
  $image->Quantize(colors=>$colors,dither=>$dither,colorspace=>$colorspace,
    'transparent-color'=>$transparent_color,measure_error=>$measure_error);
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Colormap form.
#
sub ColormapForm
{
  my(@OptionTypes);

  @OptionTypes=
  [
    'black & white',
    'dither',
    'global colormap',
    'gray',
    'kmeans',
    'measure error',
    'map to clipboard',
    'netscape color cube',
    'ordered dither',
    'posterize',
    'preserve transparent pixels',
    'segment'
  ];

  #
  # Display Colormap form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">You have a number of options for creating or changing the image <a href="$DocumentDirectory/Colormap.html" target="help">colormap</a>.  You can reduce the number of colors in your image, dither, or convert to gray colors.  To create or modify your image's colormap, check one or more options below.  Next, press <code>quantize</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',
    -value=>'quantize'), "\n";
  print "<dt>Parameter:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Parameter',
    -size=>25,-value=>'256'), "</dd><br />\n";
  print "<dt>Choose from these options:</dt>\n";
  print '<dd>', $q->checkbox_group(-name=>'Options',-values=>@OptionTypes,
    -columns=>3,-default=>'dither'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'quantize'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Transform Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Transparent Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Colorspace.html\" target=\"help\">Colorspace</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'TransparentColor',
    -value=>'none',-size=>25), "</td>\n";
  my @types=Image::Magick->QueryOption('colorspace');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Colorspace',
    -values=>[@types],-default=>'sRGB'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br /> <br /> <br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Comment.
#
sub Comment
{
  use Digest::SHA3;

  no strict 'subs';

  my($digest, $filename, $path, $remote_host);

  local(*DATA);

  umask(002);
  $path=$DocumentRoot . $DocumentDirectory . "/comments";
  $digest=Digest::SHA3->new(512);
  $digest->add($HashDigestSalt,$q->remote_addr(),time(),{},rand(),$$);
  $filename=$path . '/' . $digest->hexdigest . '.txt';
  open(DATA,">$filename") || Error('Unable to save your comments',$filename);
  $remote_host='localhost';
  $remote_host=$q->remote_host() if $q->remote_host();
  print DATA "Host: ", GetHostname($remote_host), "\n";
  print DATA "Address: ", $q->remote_addr(), "\n" if $q->remote_addr();
  print DATA "Ident: ", $q->remote_ident(), "\n" if $q->remote_ident();
  print DATA "User: ", $q->remote_user(), "\n" if $q->remote_user();
  print DATA "Name: ", $q->user_name(), "\n" if  $q->user_name();
  print DATA "Agent: ", $q->user_agent(), "\n" if $q->user_agent();
  print DATA "Time: ", scalar(localtime), "\n";
  print DATA "Comment:\n\n", $q->param('Comment'), "\n";
  close(DATA);
  #
  # Show comments.
  #
  $|=1;
  print $q->header(-charset=>'UTF-8');
  print $q->start_html(-title=>"ImageMagick Studio Comment Form",
    -style=>{-src=>"$DocumentDirectory/assets/magick-css.php"},
    -author=>$ContactInfo,-bgcolor=>'#FFFFFF',-encoding=>'UTF-8'), "\n";
  print <<XXX;
<br />
<center>
<a href="$SponsorURL" target="sponsor">
  <img src="$DocumentDirectory/images/$SponsorIcon" alt="[sponsor]" align=right border="0" vspace="45" /></a>
<img alt="ImageMagick Studio" src="$DocumentDirectory/images/magick.png" align=bottom width="114" height="118" border="0" />
</center>
<p><hr /></p>
XXX
  ;
  print "<dl>\n";
  print "<dl>\n";
  print "<dt>You said:<br />\n";
  print '<dd><ul><pre class=\"highlight\"><samp>', $q->param('Comment'),
    "</samp></pre></ul><br />\n";
  print "<dt>An administrator will review your comment soon.  Thanks.\n";
  print "</dl>\n";
  print "</dl>\n";
  Trailer(1);
}

#
# Comment form.
#
sub CommentForm
{
  #
  # Display Comment form.
  #
  $|=1;
  print $q->header(-charset=>'UTF-8');
  print $q->start_html(-title=>"ImageMagick Studio Comment Form",
    -style=>{-src=>"$DocumentDirectory/assets/magick-css.php"},
    -author=>$ContactInfo,-bgcolor=>'#FFFFFF',-encoding=>'UTF-8'), "\n";
  print <<XXX;
<br />
<center>
<a href="$SponsorURL" target="sponsor">
  <img src="$DocumentDirectory/images/$SponsorIcon" alt="[sponsor]" align=right border="0" vspace="45" /></a>
<img alt="ImageMagick Studio" src="$DocumentDirectory/images/magick.png" align=bottom width="114" height="118" border="0" />
</center>
<p><hr /></p>
If you have a comment or problem with <code>ImageMagick Studio</code>, enter
any details below and press <code>send</code>.  Be sure to include a valid e-mail
address if you require a response.
XXX
  ;
  $q->delete('Comment');
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dl>\n";
  print "<dl>\n";
  print '<dd>', $q->textarea(-class=>'form-control',-name=>'Comment',
    -columns=>50,-rows=>10,-wrap=>'horizontal'), "<br />\n";
  print "</dl>\n";
  print "</dl>\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'send'), ' your comment or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  print "<p><hr /></p>\n";
  print $q->end_html;
  exit;
}

#
# Compare image.
#
sub Compare
{
  no strict 'refs';

  use Image::Magick;
  use File::Copy;

  my($channel, $compare, $extent, @extents, $filename, $fuzz, $i, $image,
    $metric, $path, $status);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Read compare image.
  #
  if ($q->param('CompareURL')) {
    $filename=Untaint($q->param('CompareURL'));
    getstore($filename,'MagickStudio.dat');
  } else {
    $filename=Untaint($q->param('CompareFile')) if $q->param('CompareFile');
    $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
      $q->param('SessionID') if $q->param('Clipboard') eq 'on';
    copy($q->upload('CompareFile'),'MagickStudio.dat') ||
      copy(\*$filename,'MagickStudio.dat') ||
        (getstore($filename,'MagickStudio.dat') eq '200') ||
          Error('Unable to compare image',$filename);
  }
  Error('Unable to read image file',$filename)
    unless (-f 'MagickStudio.dat') && (-s 'MagickStudio.dat');
  Error('Image size exceeds maximum allowable',$filename)
    unless (-s 'MagickStudio.dat') < (1024*$MaxFilesize);
  $compare=Image::Magick->new;
  @extents=$compare->Ping("MagickStudio.dat");
  $extent=0;
  for ($i=0; $i < $#extents; $i+=4) { $extent+=$extents[$i]*$extents[$i+1]; }
  Error('Image extent exceeds maximum allowable') if $extent &&
    ($extent > (1024*$MaxImageExtent));
  $status=$compare->Read('MagickStudio.dat');
  Error("unable to read your image",$filename) if $#$compare < 0;
  unlink('MagickStudio.dat');
  Error('Image width or height differ') if $image->Get('width') ne
   $compare->Get('width');
  Error('Image width or height differ') if $image->Get('height') ne
   $compare->Get('height');
  #
  # Compare image.
  #
  $channel=$q->param('ChannelType');
  $metric=$q->param('MetricType');
  $fuzz="0.0";
  $fuzz=>$q->param('Fuzz') if $q->param('Fuzz');
  my $difference_image=$image->Compare(image=>$compare,metric=>$metric,
    channel=>$channel,fuzz=>$fuzz);
  if (ref($difference_image))
    {
      undef $image;
      $image=$difference_image;
    }
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Compare image form.
#
sub CompareForm
{
  my($action);

  #
  # Compare image form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Compare.html" target="help">compare</a> your image, press <code>Choose File</code> and select your image file or enter the Uniform Resource Locator of your image.  Next, choose the location of the compare image and the type of compare operation.  Finally, press <code>compare</code> to continue.</p>
XXX
  ;
  $action=$q->script_name() . "?CacheID=" . $q->param('CacheID') .
    ";Action=compare";
  print $q->start_multipart_form(-action=>$action,-class=>'form-horizontal');
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dt><a href=\"$DocumentDirectory/Filename.html\" target=\"help\">",
    "Filename</a>:</dt>\n";
  print '<dd>', $q->filefield(-name=>'CompareFile',-size=>50,-maxlength=>1024),
    "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/URL.html\" target=\"help\">",
    "URL</a>:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'CompareURL',
    -size=>50), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'compare'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Compare Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\">Fuzz</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Metric.html\" target=\"help\">Metric</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel Type</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,
    -value=>'0%'), "</td>\n";
  my @types=Image::Magick->QueryOption('metric');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'MetricType',
    -values=>[@types],-default=>'NCC'), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'ChannelType',
    -values=>[@channels],default=>'Default'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "</dd></dl>\n";
  print "<dt>Miscellaneous options:</dt>\n";
  print '<dd> ', $q->checkbox(-name=>'Clipboard',
    -label=>' use clipboard image as source for compare.'), "</dd>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br /> <br /> <br /> <br /> <br /> <br /> <br /> <br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Composite image.
#
sub Composite
{
  no strict 'refs';

  use Image::Magick;
  use File::Copy;

  my($color, $compose, $composite, $extent, @extents, $filename, $gravity,
     $geometry, $i, $image, $path, $opacity, $rotate, $slice, $status, $tile);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Read composite image.
  #
  if ($q->param('CompositeURL')) {
    $filename=Untaint($q->param('CompositeURL'));
    getstore($filename,'MagickStudio.dat');
  } else {
    $filename=Untaint($q->param('CompositeFile')) if $q->param('CompositeFile');
    $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
      $q->param('SessionID') if $q->param('Clipboard') eq 'on';
    copy($q->upload('CompositeFile'),'MagickStudio.dat') ||
      copy(\*$filename,'MagickStudio.dat') ||
        (getstore($filename,'MagickStudio.dat') eq '200') ||
          Error('Unable to composite image',$filename);
  }
  Error('Unable to read image file',$filename)
    unless (-f 'MagickStudio.dat') && (-s 'MagickStudio.dat');
  Error('Image size exceeds maximum allowable',$filename)
    unless (-s 'MagickStudio.dat') < (1024*$MaxFilesize);
  $composite=Image::Magick->new;
  @extents=$composite->Ping("MagickStudio.dat");
  $extent=0;
  for ($i=0; $i < $#extents; $i+=4) { $extent+=$extents[$i]*$extents[$i+1]; }
  Error('Image extent exceeds maximum allowable') if $extent &&
    ($extent > (1024*$MaxImageExtent));
  $status=$composite->Read('MagickStudio.dat');
  Error("unable to read your image",$filename) if $#$composite < 0;
  unlink('MagickStudio.dat');
  #
  # Composite image.
  #
  if (($#$image == 0) && ($#$composite > 0))
    {
      my($delay);

      #
      # Composite an animation on a background image.
      #
      $i=$#$composite-$#$image+1;
      $image=$image->Morph(frames=>$i);
      for ($i=0; $image->[$i]; $i++)
      {
        $delay=$composite->[$i]->Get('delay');
        $image->Set(delay=>$delay) if $delay;
      }
    }
  $color='none';
  $color=$q->param('BackgroundColor') if $q->param('BackgroundColor');
  $compose=$q->param('ComposeType');
  $geometry='+0+0';
  $geometry=$q->param('Geometry') if $q->param('Geometry');
  $gravity='Undefined';
  $gravity=$q->param('Gravity') if $q->param('Gravity');
  $rotate=0.0;
  $rotate=$q->param('Rotate') if $q->param('Rotate');
  $tile=0;
  $tile=$q->param('Tile') eq 'on' if $q->param('Tile');
  for ($i=0; $image->[$i]; $i++)
  {
    $slice=$composite->[$i % ($#$composite+1)];
    $slice->Resize(width=>$image->[$i]->Get('width'),
      height=>$image->[$i]->Get('height')) if $q->param('Resize') eq 'on';
    $image->[$i]->Composite(compose=>$compose,image=>$slice,gravity=>$gravity,
      geometry=>$geometry,rotate=>$rotate,color=>$color,tile=>$tile);
  }
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Composite image form.
#
sub CompositeForm
{
  my($action);

  #
  # Composite image form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Composite.html" target="help">composite</a> your image, press <code>Browse</code> and select your image file or enter the Uniform Resource Locator of your image.  Next, choose the location of the composite image and the type of composite operation.  Finally, press <code>composite</code> to continue.</p>
XXX
  ;
  $action=$q->script_name() . "?CacheID=" . $q->param('CacheID') .
    ";Action=composite";
  print $q->start_multipart_form(-action=>$action,-class=>'form-horizontal');
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dt><a href=\"$DocumentDirectory/Filename.html\" target=\"help\">",
    "Filename</a>:</dt>\n";
  print '<dd>', $q->filefield(-name=>'CompositeFile',-size=>50,
    -maxlength=>1024), "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/URL.html\" target=\"help\">",
    "URL</a>:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'CompositeURL',
    -size=>50), "</dd><br />\n";
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Offset</th>\n";
  print "<th>Gravity</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Geometry',
    -size=>25,-value=>'+0+0'), "</td>\n";
  my @types=Image::Magick->QueryOption('gravity');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Gravity',
    -values=>[@types],-default=>'Center'), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'composite'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Composite Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Blend</th>\n";
  print "<th>Compose</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Blend',-size=>25,
    -value=>'0%'), "</td>\n";
  my @types=Image::Magick->QueryOption('compose');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'ComposeType',
    -values=>[@types],-default=>'SrcOver'), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Rotate</th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">",
    "Background Color</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Rotate',-size=>25,
    -value=>'0.0'), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BackgroundColor',
    -value=>'none',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dt>Miscellaneous options:</dt>\n";
  print '<dd> ', $q->checkbox(-name=>'Tile',
    -label=>' tile across and down the image canvas.'), "</dd>\n";
  print '<dd> ', $q->checkbox(-name=>'Resize',
    -label=>' resize to fit.'),"</dd>\n";
  print '<dd> ', $q->checkbox(-name=>'Clipboard',
    -label=>' use clipboard image as source for composite.'), "</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# Create a temporary work area for image files.
#
sub CreateWorkDirectory
{
  use Digest::SHA3;

  my($check) = @_;

  my($digest, $path);

#  CheckStudioHours();
  CheckStudioStatus() if $check;
  $path=$DocumentRoot . $DocumentDirectory . '/workarea';
  chdir($path) || Error('Your image has expired',$path);
  umask(002);
  $digest=Digest::SHA3->new(512);
  $digest->add($HashDigestSalt,$q->remote_addr(),time(),{},rand(),$$);
  $path.='/' . $digest->hexdigest;
  $ENV{TMPDIR}=$path;
  mkdir($path,0775);
  chdir($path) || Error('Your image has expired',$path);
  $q->param(-name=>'Path',-value=>$path);
}

#
# Decorate image.
#
sub Decorate
{
  use Image::Magick;

  my($color, $compose, $geometry, $image, $path, $status);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Decorate image.
  #
  $compose=$q->param('ComposeType');
  $image->Set(compose=>$compose);
  $geometry='+0+0';
  $geometry=$q->param('Geometry') if $q->param('Geometry');
  $color='none';
  $color=$q->param('Color') if $q->param('Color');
  $image->Border(geometry=>$geometry,bordercolor=>$color,compose=>$compose)
    if $q->param('Option') eq 'border *';
  $image->Frame(geometry=>$geometry,fill=>$color,compose=>$compose)
    if $q->param('Option') eq 'frame *';
  $image->Raise(geometry=>$geometry,raise=>'true')
    if $q->param('Option') eq 'raise *';
  $image->Raise(geometry=>$geometry,raise=>'False')
    if $q->param('Option') eq 'sunken *';
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Decorate image form.
#
sub DecorateForm
{
  my @OptionTypes=
  [
    'border *',
    'frame *',
    'raise *',
    'sunken *'
  ];

  #
  # Display Decorate form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Decorate.html" target="help">decorate</a> your image with a border or frame, set your options below and press <code>decorate</code>.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dt>Decoration geometry:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Geometry',
    -size=>25,-value=>'15x15+3+3'), "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Color</a>:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Color',-size=>25,
    -value=>'gray'), "</dd><br />\n";
  print "<dt>Choose from these decorations:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>5,-default=>'frame *'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'decorate'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Decorate Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Compose</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('compose');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'ComposeType',
    -values=>[@types],-default=>'SrcOver'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br /> <br /> <br /> <br /> <br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Download the image in the same or differing image format.
#
sub Download
{
  use Image::Magick;

  my($basename, $coalesce, $format, $height, $hostname, $i, $image, $montage,
     $path, $prefix, $size, $status, $url, $username, $value, $width, $x, $y);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Write image.
  #
  CreateWorkDirectory(undef);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  #
  # Convert the image to the selected format.
  #
  $image->Set(page=>'0x0+0+0') if $q->param('Repage') eq 'on';
  $image->Strip() if $q->param('Strip') eq 'on';
  $value=$q->param('Type');
  $image->Set(type=>$value) if $value ne 'Implicit';
  $value=$q->param('Channel');
  $image->Separate($value) unless $value eq 'All';
  $image->Set(font=>$DefaultFont);
  $value=$q->param('Compress');
  $image->Set(compression=>$value) if $value ne 'Default';
  $value=$q->param('Page'); $value=~s/ //g;
  $image->Set(page=>$value) if length($value) > 0;
  $value=$q->param('Delay');
  $image->Set(delay=>$value) if length($value) > 0;
  $value=$q->param('Depth');
  $image->Set(depth=>$value) if length($value) > 0;
  $value=$q->param('Dispose');
  $image->Set(dispose=>$value) unless $value eq 'Undefined';
  $value=$q->param('Loop');
  $image->Set(loop=>$value) if length($value) > 0;
  $value=$q->param('Quality');
  $image->Set(quality=>$value) if length($value) > 0;
  $value=$q->param('Interlace');
  $image->Set(interlace=>$value);
  $value=$q->param('Preview');
  $image->Set(preview=>$value);
  $image->Set(pointsize=>10);
  $image->Set(adjoin=>1);
  $image->Set(adjoin=>0) if $q->param('Option') eq 'single file';
  $image->Set(colorspace=>'CMYK') if
    $q->param('CMYK') && ($q->param('CMYK') eq 'on');
  $value=$q->param('Alpha');
  $image->Set(alpha=>$value) unless $value eq 'Undefined';
  $value=$q->param('Comment');
  $image->Comment($value) if length($value) > 0;
  if ($q->param('Option') eq 'append')
    {
      my($append_image);

      $value='True';
      $value='False' if $q->param('Stack') eq 'on';
      $image=$image->Append(stack=>$value);
      if (ref($append_image))
        {
          #
          # Append the image sequence.
          #
          undef $image;
          $image=$append_image;
        }
    }
  if ($q->param('Option') eq 'coalesce')
    {
      my($coalesce_image);

      $coalesce_image=$image->Coalesce();
      if (ref($coalesce_image))
        {
          #
          # Coalesce the image sequence.
          #
          undef $image;
          $image=$coalesce_image;
        }
    }
  if ($q->param('Option') eq 'smush')
    {
      my($offset,$smush_image);

      $offset=$q->param('offset');
      $value='True';
      $value='False' if $q->param('Stack') eq 'on';
      $smush_image=$image->Smush(stack=>$value,offset=>$offset);
      if (ref($smush_image))
        {
          #
          # Smush the image sequence.
          #
          undef $image;
          $image=$smush_image;
        }
    }
  $prefix='';
  $prefix=$q->param('Option') . ':' if
    ($q->param('Option') eq 'histogram') || ($q->param('Option') eq 'preview');
  $basename=$q->param('Name');
  $format='png';
  if (length($q->param('Passphrase')) > 0)
    {
      my($passphrase);

      $passphrase=$q->param('Passphrase');
      $image->Encipher($passphrase);
    }
  $coalesce=$image->Coalesce();
  if ($#$coalesce > 0)
    {
      $format='gif';
      $coalesce->Set(loop=>0,delay=>800) if $coalesce->Get('iterations') == 1;
      $image=$coalesce if $q->param('Coalesce') eq 'on';
    }
  $status=$coalesce->Write("$basename.$format");
  Error($status) if "$status";
  $format=$q->param('Magick');
  $format=$q->param('Format') if $q->param('Format');
  $format='jpg' if $format =~ /jpeg/;
  $image->Set(magick=>$format);
  for ($i=0; $image->[$i]; $i++)
  { $image->[$i]->Set(scene=>$i); }
  if ($q->param('Option') eq 'clipboard')
    {
      my($clipboard, $filename);

      #
      # Paste file to clipboard.
      #
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID');
      $status=$image->Write(filename=>"$filename.mpc");
      Error($status) if "$status";
      $clipboard=$image->Clone();
      $clipboard->Resize($IconSize);
      $status=$clipboard->Write("$filename.gif");
      Error($status) if "$status";
    }
  if ($#$image > 0)
    {
      $status=$image->Write(filename=>"$prefix$basename.$format",adjoin=>1);
      Error($status) if "$status";
      $status=$image->Write(filename=>'Animate.gif',adjoin=>1);
      Error($status) if "$status";
    }
  if (($q->param('Option') ne 'single file') || ($#$image == 0))
    {
      $status=$image->Write("$prefix$basename.$format");
      Error($status) if "$status";
    }
  else
    {
      my($filename);

      $filename="$prefix$basename" . '%d.' . "$format";
      $status=$image->Write(filename=>$filename);
      Error($status) if "$status";
    }
  if (($q->param('Option') eq 'histogram') ||
      ($q->param('Option') eq 'preview'))
    {
      undef @$image;
      $status=$image->Read("$basename.$format");
      Error($status) if $#$image < 0;
      $status=$image->Write("$basename.$format");
      Error($status) if "$status";
    }
  #
  # Label image.
  #
  for ($i=0; $image->[$i]; $i++)
  {
    $image->[$i]->Label($image->[$i]->Get('filename'));
    next if $i == 0;
    $image->[$i]->Label($image->[$i]->Get('scene')) if
      $image->[0]->Get('filename') eq $image->[$i]->Get('filename');
  }
  $montage=$image->Montage(background=>'#efefef',borderwidth=>0,
    geometry=>'120x120+2+2>',gravity=>'Center',font=>$DefaultFont,
    fill=>'black',transparent=>'#efefef');
  Error($montage) if !ref($montage);
  $montage->Set(page=>'0x0+0+0');
  $status=$montage->Write('MagickStudio.gif');
  Error($status) if "$status";
  #
  # Display images to the user.
  #
  $url=substr($q->param('Path'),length($DocumentRoot));
  print <<XXX;
<p>Here is your converted image (or images).  Click on any image to view or precede your click by the shift key to download it to your local area or press <code>upload</code> to transfer the image to a remote site.</p>
<center>
XXX
  ;
  if ($#$image > 0)
    {
      #
      # Display animated image.
      #
      ($width,$height)=$image->Get('width','height');
      print <<XXX;
<p><a href="$url/$basename.$format"> <img alt="$basename.$format" src="$url/Animate.gif" width=$width height=$height border="0" /></a></p>
XXX
  ;
    }
  ($width,$height)=$montage->Get('width','height');
  print <<XXX;
<p><img ismap usemap=#Montage src="$url/MagickStudio.gif" width=$width height=$height border="0" /></p>
<map name=Montage>
XXX
  ;
  $montage->Get('montage')=~/(\d+\.*\d*)x(\d+\.*\d*)\+(\d+\.*\d*)\+(\d+\.*\d*)/;
  $width=$1;
  $height=$2;
  $x=$3;
  $y=$4;
  for (split(/\xff/,$montage->Get('directory')))
  {
    print "  <area href=\"$url/$_\"", " shape=rect coords=$x,$y,",
      $x+$width-1, ',', $y+$height-1, " target=\"", rand($timer+$$), "\">\n";
    $x+=$width;
    if ($x >= $montage->Get('width'))
      {
        $x=0;
        $y+=$height;
      }
  }
  $hostname=$q->server_name();
  print <<XXX;
</map>
<br /> <br /> <br />
</center>
XXX
  ;
  print "* <i>this image was saved to the ImageMagick Studio clipboard.</i><br />"
    if $q->param('Option') eq 'clipboard';
  #
  # Image upload form.
  #
  RestoreQueryState($q->param('SessionID'),$q->param('Path'),'FileTransfer');
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',
    -value=>'upload'), "\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'upload'), ' your image to a remote site or ', $q->reset(
    -name=>'reset',-class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Upload Properties</legend>\n";
  print "<dl>\n";
  $hostname=GetHostname($q->remote_host());
  print "<dt><a href=\"$DocumentDirectory/Upload.html\" target=\"help\">FTP server name</a>:\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Hostname',
    -size=>50,-value=>$hostname), "<br />\n";
  print "<dt><a href=\"$DocumentDirectory/Upload.html\" target=\"help\">Account name</a>:\n";
  $username='anonymous';
  $username=$q->remote_user() if $q->remote_user();
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Username',
    -size=>25,-value=>$username), "<br />\n";
  print "<dt><a href=\"$DocumentDirectory/Upload.html\" target=\"help\">Account password</a>:\n";
  print '<dd>', $q->password_field(-name=>'Password',-size=>25), "<br />\n";
  print "<dt><a href=\"$DocumentDirectory/Upload.html\" target=\"help\">Upload directory</a>:\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Directory',
    -size=>50), "<br />\n";
  print "<dt><a href=\"$DocumentDirectory/Upload.html\" target=\"help\">Filename</a>:\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Filename',
    -size=>50, -value=>"$basename.$format"), "<br />\n";
  print "</dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  Trailer(undef);
}

#
# Download image form.
#
sub DownloadForm
{
  my($format, @formats, $image, @OptionTypes, $path, $status);

  @OptionTypes=
  [
    'append',
    'clipboard',
    'coalesce',
    'histogram',
    'multi-frame file',
    'preview',
    'single file',
    'smush'
  ];

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Display Download form.
  #
  Header(GetTitle($image));
  print <<XXX;
<p class="lead magick-description">Choose an <a href="$DocumentDirectory/Download.html" target="help">output</a> image format and set any optional image attributes below.  Some attributes are only relevant to specific output formats.  Next, press <code>output</code> to convert your image to the selected format.  The image is converted and you are given an opportunity to download it to your local area.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'output'),
    "\n";
  print "<dt><a href=\"$DocumentDirectory/Format.html\" target=\"help\">Format</a>:</dt>\n";
  $format=$q->param('Magick');
  @formats=$image->QueryFormat();
  print '<dd>', $q->scrolling_list(-class=>'form-control',-name=>'Format',
    -values=>[@formats],-size=>7,-default=>$format), "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/Storage.html\" target=\"help\">Storage type</a>:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>3,-default=>'multi-frame file'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'output'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Download Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Image Type</th>\n";
  print "<th>Compress</th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel</a></th>\n";
  print "<th>Alpha</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('type');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Type',
    -values=>[@types]), "</td>\n";
  my @types=Image::Magick->QueryOption('compress');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Compress',-values=>[@types]), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Channel',
    -values=>[@channels],-default=>'All'), "</td>\n";
  my @types=Image::Magick->QueryOption('Alpha');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Alpha',
    -values=>[@types],-default=>'Undefined'), "</td>\n";
  print "</tr>\n";
  print "</table><br />\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Dispose</th>\n";
  print "<th><a href=\"$DocumentDirectory/Interlace.html\" target=\"help\">Interlace</a></th>\n";
  print "<th>Preview</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('dispose');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Dispose',
    -values=>[@types],-default=>'Undefined'), "</td>\n";
  my @types=Image::Magick->QueryOption('interlace');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Interlace',
    -values=>[@types],-default=>'None'), "</td>\n";
  my @types=Image::Magick->QueryOption('preview');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Preview',
    -values=>[@types]), "</td>\n";
  print "</tr>\n";
  print "</table><br />\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Delay.html\" target=\"help\">Delay</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Loop.html\" target=\"help\">Loop</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Quality.html\" target=\"help\">Quality</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Delay',-size=>15,
    -value=>$image->Get('delay')), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Loop',-size=>15,
    -value=>$image->Get('loop')), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Quality',-size=>15,
    -value=>$image->Get('quality')), "</td>\n";
  print "</tr>\n";
  print "</table><br />\n";
  print "<dt>Image Depth</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Depth',-size=>25,
    -value=>$image->Get('depth')), "</dd><br />\n";
  print "<dt>Smush Offset</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Offset',-size=>25,
    -value=>2), "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/Page.html\" target=\"help\">",
    "Page Geometry</a></dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Page',-size=>25),
    "</dd><br />\n";
  print "<dt><a href=\"$DocumentDirectory/Passphrase.html\" target=\"help\">",
    "Passphrase</a></dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Passphrase',
    -size=>25), "</dd><br />\n";
  print "<dt>Comment:</dt>\n";
  print '<dd>', $q->textarea(-class=>'form-control',-name=>'Comment',
    -columns=>50,-rows=>3,-value=>$image->Get('comment')), "</dd><br />\n";
  print "<dt> Miscellaneous options:</dt>\n";
  print '<dd>', $q->checkbox(-name=>'Repage',
    -label=>' reset page geometry.'), "</dd>\n";
  print '<dd>', $q->checkbox(-name=>'Coalesce',
    -checked=>'true',-label=>' coalesce multi-frame images.'), "</dd>\n";
  print '<dd>', $q->checkbox(-name=>'Strip',
    -label=>' strip image of any comments or profiles.'), "</dd>\n";
  print '<dd> ', $q->checkbox(-name=>'CMYK',
    -label=>' save image as CMYK pixels (JPEG, TIFF, PS, PDF, PSD)'), "</dd>\n";
  print '<dd> ', $q->checkbox(-name=>'Stack',
    -label=>' stack images left-to-right (when storage type is append)'),
    "</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(undef);
}

#
# Draw image.
#
sub Draw
{
  use Image::Magick;

  my($antialias, $fill, $image, $path, $points, $primitive, $rotate, $scale,
    $skew_x, $skew_y, $status, $stroke, $strokewidth, $translate, $x, $y);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Draw image.
  #
  $antialias='false';
  $antialias='true' if $q->param('Antialias') eq 'on';
  $fill='none';
  $fill=$q->param('Fill') if $q->param('Fill');
  $points='+10+10 +60+60';
  $points=$q->param('Coordinates') if $q->param('Coordinates');
  $primitive=$q->param('Primitive');
  $rotate=0.0;
  $rotate=$q->param('Rotate') if $q->param('Rotate');
  $scale='0.0, 0.0';
  $scale=$q->param('Scale') if $q->param('Scale');
  $skew_x=0.0;
  $skew_x=$q->param('SkewX') if $q->param('SkewX');
  $skew_y=0.0;
  $skew_y=$q->param('SkewY') if $q->param('SkewY');
  $stroke='none';
  $stroke=$q->param('Stroke') if $q->param('Stroke');
  $strokewidth=1;
  $strokewidth=$q->param('StrokeWidth') if $q->param('StrokeWidth');
  $translate='0.0, 0.0';
  $translate=$q->param('Translate') if $q->param('Translate');
  $x=0;
  $y=0;
  ($x,$y)=split(/[ ,]+/,$q->param('Translate')) if $q->param('Translate');
  if (!$q->param('Tile') || ($q->param('Tile') ne 'on'))
    {
      $image->Draw(primitive=>$primitive,fill=>$fill,stroke=>$stroke,
        strokewidth=>$strokewidth,points=>$points,x=>$x,y=>$y,
        translate=>$translate,scale=>$scale,rotate=>$rotate,skewX=>$skew_x,
        skewY=>$skew_y,antialias=>$antialias);
    }
  else
    {
      my($filename, $tile);

      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $tile=Image::Magick->new;
      $status=$tile->Read($filename);
      Error($status) if $#$tile < 0;
      $image->Draw(primitive=>$primitive,fill=>$fill,stroke=>$stroke,
        strokewidth=>$strokewidth,tile=>$tile,points=>$points,x=>$x,y=>$y,
        translate=>$translate,scale=>$scale,rotate=>$rotate,skewX=>$skew_x,
        skewY=>$skew_y,antialias=>$antialias);
    }
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Draw image form.
#
sub DrawForm
{
  #
  # Display draw form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Draw.html" target="help">draw</a> on your image, choose a drawing primitive, define it with coordinates, and press <code>draw</code>.  There are additional optional attributes below.  Set them as appropriate.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print "<dt>Primitive:</dt>\n";
  my @types=Image::Magick->QueryOption('primitive');
  print '<dd>', $q->popup_menu(-class=>'form-control',-name=>'Primitive',
    -values=>[@types],-default=>'Line'), "</dd><br />\n";
  print "<dt>Coordinates:</dt>\n";
  print '<dd>', $q->textarea(-class=>'form-control',-name=>'Coordinates',
    -columns=>50,-rows=>2,-value=>'+10+10  +60+60',-wrap=>'horizontal'),
    "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'draw'), ' on your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Draw Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Fill Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Stroke Color</a></th>\n";
  print "<th>Stroke Width</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Fill',
    -value=>'white',-size=>25),"</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Stroke',
    -value=>'none',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'StrokeWidth',
    -size=>25,-value=>'1'), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Translate</th>\n";
  print "<th>Scale</th>\n";
  print "<th>Rotate</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Translate',
    -value=>'0.0, 0.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Scale',
    -value=>'1.0, 1.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Rotate',
    -value=>'0.0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Skew X</th>\n";
  print "<th>Skew Y</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SkewX',
    -value=>'0.0',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SkewY',
    -value=>'0.0',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "<dt>Miscellaneous options:</dt>\n";
  print '<dd> ', $q->checkbox(-name=>'Tile',
    -label=>' paint the drawing primitive with the clipboard image.'),
    "</dd>\n";
  print '<dd>', $q->checkbox(-name=>'Antialias',
    -label=>' antialias text.',-checked=>'true'), "</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# Effects image.
#
sub Effects
{
  use Image::Magick;

  my($channel, $filename, $image, $parameter, $path, $status);

  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Effects image.
  #
  $parameter=$q->param('Parameter');
  $channel=$q->param('Channel');
  $image->Set('virtual-pixel'=>$q->param('VirtualPixelMethod')) if
    $q->param('VirtualPixelMethod');
  $image->Set(label=>$q->param('Label')) if $q->param('Label');
  $image->AdaptiveBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'adaptive blur *';
  $image->AdaptiveSharpen(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'adaptive sharpen *';
  $image->BilateralBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'bilateral blur *';
  $image->BlackThreshold(geomery=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'black threshold *';
  $image->Blur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'blur *';
  $image->Charcoal("$parameter") if $q->param('Option') eq 'charcoal drawing *';
  if ($q->param('Option') eq 'clut')
    {
      my($channel, $source);

      $channel=$q->param('Channel');
      $source=Image::Magick->new;
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $status=$source->Read($filename);
      Error($status) if $#$source < 0;
      if ($channel eq 'All')
        { $image->Clut(image=>$source); }
      else
        { $image->Clut(image=>$source,channel=>$channel); }
      Error($image) if !ref($image);
    }
  $image->ConnectedComponents("$parameter") if $q->param('Option') eq
    'connected components *';
  if ($q->param('Option') eq 'convolve *')
    {
      my(@coefficients);

      @coefficients=split(/[ ,]+/,$parameter);
      $image->Convolve(\@coefficients);
    }
  $image->Despeckle() if $q->param('Option') eq 'despeckle';
  if ($q->param('Option') eq 'distort *')
    {
      my(@points, $method);

      @points=split(/[ ,]+/,$parameter);
      $method=$q->param('DistortType');
      $image->Distort(method=>$method,points=>\@points);
    }
  if ($q->param('Option') eq 'evaluate *')
    {
      my(@values, $operator);

      @values=split(/[ ,]+/,$parameter);
      $operator=$q->param('EvaluateType');
      $image->Evaluate(operator=>$operator,value=>\@values);
    }
  if ($q->param('Option') eq 'function *')
    {
      my(@parameters, $function);

      @parameters=split(/[ ,]+/,$parameter);
      $function=$q->param('FunctionType');
      $image->Function(function=>$function,parameters=>\@parameters);
    }
  $image->CannyEdge("$parameter") if $q->param('Option') eq 'canny edge *';
  $image->Edge("$parameter") if $q->param('Option') eq 'edge detect *';
  $image->Emboss(geometry=>$parameter) if $q->param('Option') eq 'emboss *';
  $image->ForwardFourierTransform("$parameter") if
    $q->param('Option') eq 'forward Fourier transform';
  if ($q->param('Option') eq 'Channel F(x) *')
    {
      my($channel);

      $channel=$q->param('Channel');
      if ($q->param('Clipboard') ne 'on')
        {
          my $fx;

          if ($channel eq 'All')
            { $image = $image->ChannelFx(expression=>$parameter); }
          else
            { $image = $image->ChannelFx(channel=>$channel,
              expression=>$parameter); }
          Error($image) if !ref($image);
        }
      else
        {
          my($source);

          #
          # Read clipboard image.
          #
          $source=Image::Magick->new;
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc';
          $status=$source->Read($filename);
          Error($status) if $#$source < 0;
          if ($channel eq 'All')
            { $image->ChannelFx(image=>$source,expression=>$parameter); }
          else
            {
              $image->ChannelFx(image=>$source,channel=>$channel,
                expression=>$parameter);
            }
          Error($image) if !ref($image);
        }
    }
  if ($q->param('Option') eq 'F(x) *')
    {
      my($channel);

      $channel=$q->param('Channel');
      if ($q->param('Clipboard') ne 'on')
        {
          my $fx;

          if ($channel eq 'All')
            { $image = $image->Fx(expression=>$parameter); }
          else
            { $image = $image->Fx(channel=>$channel,expression=>$parameter); }
          Error($image) if !ref($image);
        }
      else
        {
          my($source);

          #
          # Read clipboard image.
          #
          $source=Image::Magick->new;
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc';
          $status=$source->Read($filename);
          Error($status) if $#$source < 0;
          if ($channel eq 'All')
            { $image->Fx(image=>$source,expression=>$parameter); }
          else
            {
              $image->Fx(image=>$source,channel=>$channel,
                expression=>$parameter);
            }
          Error($image) if !ref($image);
        }
    }
  $image->GaussianBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'gaussian blur *';
  if ($q->param('Option') eq 'hald-clut')
    {
      my($channel, $source);

      $channel=$q->param('Channel');
      $source=Image::Magick->new;
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $status=$source->Read($filename);
      Error($status) if $#$source < 0;
      if ($channel eq 'All')
        { $image->HaldClut(image=>$source); }
      else
        { $image->HaldClut(image=>$source,channel=>$channel); }
      Error($image) if !ref($image);
    }
  $image->HoughLine("$parameter") if $q->param('Option') eq 'hough line *';
  $image->Implode("$parameter") if $q->param('Option') eq 'implode *';
  $image->Integral() if $q->param('Option') eq 'integral';
  $image->InverseFourierTransform("$parameter") if
    $q->param('Option') eq 'inverse Fourier transform';
  $image->Kuwahara(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'kuwahara *';
  $image->MeanShift("$parameter") if $q->param('Option') eq 'mean shift *';
  $image->Mode("$parameter") if $q->param('Option') eq 'mode *';
  if ($q->param('Option') eq 'morph *')
    {
      my($morph_image);

      if (($#$image+1) == 1)
        {
          #
          # Read clipboard image.
          #
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc';
          $status=$image->Read($filename);
          Error($status) if $#$image < 0;
        }
      $morph_image=$image->Morph(frames=>$parameter);
      if (ref($morph_image))
        {
          #
          # Replace image sequence with morph sequence.
          #
          undef $image;
          $image=$morph_image;
        }
    }
  if ($q->param('Option') eq 'morphology *')
    {
      my($method);

      $method=$q->param('MorphologyMethod');
      $image->Morphology(kernel=>$parameter,method=>$method,channel=>$channel);
    }
  if ($q->param('Option') eq 'mosaic')
    {
      my($mosaic_image);

      if (($#$image+1) == 1)
        {
          #
          # Read clipboard image.
          #
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc';
          $status=$image->Read($filename);
          Error($status) if $#$image < 0;
        }
      $mosaic_image=$image->Mosaic();
      if (ref($mosaic_image))
        {
          #
          # Replace image sequence with mosaic sequence.
          #
          undef $image;
          $image=$mosaic_image;
        }
    }
  $image->MotionBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'motion blur *';
  $image->MedianFilter("$parameter") if
    $q->param('Option') eq 'median filter *';
  $image->OilPaint("$parameter") if $q->param('Option') eq 'oil paint *';
  if ($q->param('Option') eq 'color-matrix *')
    {
      my(@coefficients);

      @coefficients=split(/[ ,]+/,$parameter);
      $image->ColorMatrix(\@coefficients);
    }
  $image->RangeThreshold(geomery=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'range threshold *';
  $image->ReduceNoise("$parameter") if $q->param('Option') eq 'reduce noise *';
  $image->RotationalBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'rotational blur *';
  $image->SelectiveBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq '-class=>"checkbox",selective blur *';
  $image->SepiaTone("$parameter") if $q->param('Option') eq 'sepia tone *';
  $image->Shade(geometry=>$parameter,gray=>'false')
    if $q->param('Option') eq 'shade *';
  $image->Shade(geometry=>$parameter,gray=>'true')
    if $q->param('Option') eq 'gray shade *';
  if ($q->param('Option') eq 'shadow *')
    {
      my($mosaic_image, $shadow_image);

      #
      # Simulate an image shadow
      #
      $shadow_image=$image->Clone();
      $shadow_image->Set(background=>$q->param('BackgroundColor'));
      $shadow_image->Shadow("$parameter");
      $shadow_image->Set(background=>'none');
      push(@$shadow_image,@$image);
      $mosaic_image=$shadow_image->Mosaic();
      if (ref($mosaic_image))
        {
          #
          # Replace image sequence with mosaic sequence.
          #
          undef $image;
          $image=$mosaic_image;
        }
    }
  $image->Sharpen(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'sharpen *';
  $image->Sketch("$parameter") if $q->param('Option') eq 'sketch *';
  $image->Solarize("$parameter") if $q->param('Option') eq 'solarize *';
  $image->Spread("$parameter") if $q->param('Option') eq 'spread *';
  if ($q->param('Option') eq 'stegano *')
    {
      my($clipboard);

      #
      # Read clipboard image.
      #
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $clipboard=Image::Magick->new(size=>"256x256+$parameter");
      $status=$clipboard->Read($filename);
      Error("unable to stegano image, no clipboard image") if $#$clipboard < 0;
      $image->Stegano(image=>$clipboard);
    }
  if ($q->param('Option') eq 'stereo')
    {
      my($stereo);

      $stereo=$image->Clone();
      $stereo->Roll('+4+4');
      $image->Stereo(image=>$stereo);
    }
  $image->Swirl("$parameter") if $q->param('Option') eq 'swirl *';
  $image->AdaptiveThreshold("$parameter") if
    $q->param('Option') eq 'adaptive threshold *';
  $image->AutoThreshold() if $q->param('Option') eq 'auto-threshold';
  $image->Threshold(threshold=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'threshold *';
  $image->Tint(fill=>$q->param('FillColor'),opacity=>$parameter) if
    $q->param('Option') eq 'tint';
  $image->UnsharpMask(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'unsharp mask *';
  $image->Vignette(geometry=>"$parameter",background=>
    $q->param('BackgroundColor')) if $q->param('Option') eq 'vignette *';
  $image->Wave("$parameter") if $q->param('Option') eq 'wave *';
  $image->WaveletDenoise("$parameter") if
    $q->param('Option') eq 'wavelet denoise *';
  $image->WhiteThreshold(threshold=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'white threshold *';
  $image->Set(page=>'0x0+0+0') if $q->param('Repage') eq 'on';
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Effects form.
#
sub EffectsForm
{
  my @OptionTypes=
  [
    'adaptive blur *',
    'adaptive sharpen *',
    'adaptive threshold *',
    'auto-threshold',
    'bilateral blur *',
    'black threshold *',
    'blur *',
    'canny edge *',
    'despeckle',
    'edge detect *',
    'emboss *',
    'gaussian blur *',
    'gray shade *',
    'hough line *',
    'kuwahara *',
    'mean shift *',
    'median filter *',
    'mode *',
    'motion blur *',
    'range threshold *',
    'reduce noise *',
    'rotational blur *',
    'selective blur *',
    'shade *',
    'sharpen *',
    'spread *',
    'threshold *',
    'unsharp mask *',
    'white threshold *'
  ];

  #
  # Display Effects form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Effects.html" target="help">effect</a> your image, enter your effects parameter and method.  Note, only methods denoted with an asterisk require a parameter value.  Next, press <code>effect</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'effect'),
    "\n";
  print "<dt>Parameter:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Parameter',
    -size=>25,-value=>'0.0x1.0'), "</dd><br />\n";
  print "<dt>Choose from these effects:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>3,-default=>'sharpen'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'effect'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Effects Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Virtual Pixel Method</th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @methods=Image::Magick->QueryOption('virtual-pixel');
  print '<td>', $q->popup_menu(-class=>'form-control',
    -name=>'VirtualPixelMethod',-values=>[@methods]), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Channel',
    -values=>[@channels],-default=>'Default'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Enhance image.
#
sub Enhance
{
  use Image::Magick;

  my($channel, $image, $parameter, $path, $status);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Enhance image.
  #
  $parameter=$q->param('Parameter');
  $channel=$q->param('Channel');
  if ($q->param('clipboard as CLUT'))
    {
      my($clut, $filename);

      #
      # Use clipboard image as CLUT.
      #
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $clut=Image::Magick->new;
      $status=$clut->Read($filename);
      Error($status) if $#$clut < 0;
      $image->Remap(image=>$clut,channel=>$channel);
    }
  $image->Set('virtual-pixel'=>$q->param('VirtualPixelMethod')) if
    $q->param('VirtualPixelMethod');
  $image->AutoGamma() if $q->param('Option') eq 'auto-gamma';
  $image->AutoLevel() if $q->param('Option') eq 'auto-level';
  $image->BrightnessContrast(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'brightness-contrast *';
  $image->CLAHE("$parameter") if $q->param('Option') eq 'calhe *';
  $image->Contrast(sharpen=>'true') if $q->param('Option') eq 'spiff';
  $image->Contrast(sharpen=>'false') if $q->param('Option') eq 'dull';
  $image->ContrastStretch(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'contrast-stretch *';
  $image->Equalize(channel=>$channel) if $q->param('Option') eq 'equalize';
  $image->Gamma(gamma=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'gamma *';
  $image->Level(levels=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'level *';
  $image->LinearStretch($parameter) if $q->param('Option') eq
    'linear-stretch *';
  $image->Modulate(hue=>$parameter) if $q->param('Option') eq 'hue *';
  $image->Modulate(saturation=>$parameter)
    if $q->param('Option') eq 'saturation *';
  $image->Modulate(brightness=>$parameter)
    if $q->param('Option') eq 'brightness *';
  $image->Normalize(channel=>$channel) if $q->param('Option') eq 'normalize';
  $image->Negate(channel=>$channel) if $q->param('Option') eq 'negate';
  $image->SigmoidalContrast(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'sigmoidal-contrast *';
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Enhance form.
#
sub EnhanceForm
{
  my @OptionTypes=
  [
    'auto-gamma',
    'auto-level',
    'brightness *',
    'brightness-contrast *',
    'clahe *',
    'clipboard as CLUT',
    'contrast-stretch *',
    'dull',
    'equalize',
    'gamma *',
    'hue *',
    'level *',
    'linear-stretch *',
    'negate',
    'normalize',
    'saturation *',
    'spiff',
    'sigmoidal-contrast *'
  ];

  #
  # Display Enhancement form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p>To <a href="$DocumentDirectory/Enhance.html" target="help">enhance</a> your image, enter your enhancement parameter and method.  Note, only methods denoted with an asterisk require a parameter value.  Next, press <code>enhance</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',
    -value=>'enhance'), "\n";
  print "<dt>Parameter:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Parameter',
    -size=>25,-value=>'1.6'), "</dd><br />\n";
  print "<dt>Choose from these enhancements:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>3,-default=>'gamma *'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'enhance'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Enhance Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Virtual Pixel Method</th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @methods=Image::Magick->QueryOption('virtual-pixel');
  print '<td>', $q->popup_menu(-class=>'form-control',
    -name=>'VirtualPixelMethod',-values=>[@methods]), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Channel',
    -values=>[@channels],-default=>'Default'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Display an error.
#
sub Error
{
  my($message,$qualifier) = @_;

  Header($message) unless $header;
  $qualifier="" unless $qualifier;
  print <<XXX;
<center>
<img src="$DocumentDirectory/images/stop.png" width="48" height="48" border="0" />
</center>
<br /> <br />
<dl>
<dt><font face="Arial,Helvetica" size=+2>$message:</font>
<br />
<dd><font face="Arial,Helvetica" size=+1>$qualifier</font>
<br />
<dd><font face="Arial,Helvetica" size=+0>$!</font>
</dl>
<br /> <br />
<center>
<img src="$DocumentDirectory/images/stop.png" width="48" height="48" border="0" />
</center>
<br />
<br />
<br />
Press <code>Back</code> to correct the error or press a tab above to continue.
XXX
  ;
  Trailer(0);
  die $message;
}

#
# Expire files in the workarea that are older than some threshold.
#
sub ExpireFiles
{
  my($path, $age) = @_;

  use File::Path;

  my(@files, $number_files);

  local(*DIR);

  chdir($path) || Error('Your image has expired',$path);
  opendir(DIR,".");
  @files=readdir(DIR);
  closedir(DIR);
  $number_files=$#files+1;
  for (@files)
  {
    next if /^\./;
    next if /^index.html/;
    next if (time()-(stat($_))[9]) < $age;
    rmtree($_,0,1);
    $number_files--;
  }
  ExpireFiles($path,$age/2) if
    ($number_files > $MaxWorkFiles) && ($age > $MinExpireAge);
}

#
# Fetch all the images from an HTTP directory.
#
sub PursueLink
{
  my($prefix, $type, $quote, $url, $base, $depth) = @_;

  $url=url($url,$base)->abs;
  $prefix . $quote . FetchImages($url,$type,$depth) . $quote;
}

sub FetchImages
{
  my($url, $type, $depth) = @_;

  use URI::URL;
  use LWP::UserAgent;
  use LWP::MediaTypes qw(media_suffix);

  my($base, $content, $content_type, $name, $plain_url, $result, $seen,
    $suffix);

  $url=url($url) unless ref($url);
  if ($depth == 0)
    {
      #
      # Limit to URLs below this one.
      #
      $user_agent=new LWP::UserAgent;
      $user_agent->agent('MagickStudio/1.0 ' . $user_agent->agent);
      $user_agent->env_proxy if $ENV{'http_proxy'};
      $prefix=url($url);
      eval
      {
        $prefix->eparams(undef);
        $prefix->equery(undef);
      };
      $_=$prefix->epath;
      s|[^/]+$||;
      $prefix->epath($_);
      $prefix=$prefix->as_string;
      %seen=();
      $length=0;
      FetchImages($url,$type,$depth+1);
      return(undef);
    }
  $type||='a';
  $type='img' if $type eq 'body';
  $depth||=0;
  return($url->as_string) if $url->scheme eq 'mailto';
  $plain_url=$url->clone;
  $plain_url->frag(undef);
  $seen=$seen{$plain_url->as_string};
  if ($seen)
    {
      my($fragment);

      #
      # We have already seen this document.
      #
      $fragment=$url->frag;
      $seen.="#$fragment" if defined($fragment);
      return($seen);
    }
  return($url) if $depth > 2;  # no recursion
  return $url->as_string if ($type ne 'img') and
    ($url->as_string !~ /^\Q$prefix/o);
  #
  # Fetch image.
  #
  $result=$user_agent->request(HTTP::Request->new(GET=>$url));
  if (!$result->is_success)
    {
      $seen{$plain_url->as_string}="*BAD*";
      return("*BAD*");
    }
  $content=$result->content;
  $content_type=$result->content_type;
  #
  # Construct an image name.
  #
  $url=$result->request->url;
  $url=url($url) unless ref($url);
  $name=$url->path;
  $name=~s|.*/||;
  $name=~s|\..*||;
  $name="index" unless length($name);
  $suffix=media_suffix($content_type);
  $name.=".$suffix" if $suffix;
  $seen{$plain_url->as_string}=$name;
  if ($content_type ne "text/html")
    {
      local(*FILE);

      #
      # Save document to disk.
      #
      return($name) if $name eq 'back.gif';
      return($name) if $name eq 'blank.gif';
      return($name) if $name eq 'image2.gif';
      $length+=$result->content_length;
      Error('Image size exceeds maximum allowable',$plain_url->as_string)
        unless $length < (1024*$MaxFilesize);
      open(FILE,">$name") || Error('Unable to write image file',$name);
      binmode(FILE);
      print FILE $content;
      close(FILE);
      return($name);
    }
  #
  # Follow the links in this HTML document.
  #
  $base=$result->base;
  $content=~s/(<\s*(img|a|body)\b[^>]+\b(?:src|href|background)\s*=\s*)(["']?)([^>\s]+)\3/PursueLink($1,lc($2),$3,$4,$base,$depth+1)/gie;       #";
  return($name);
}

#
# File transfer the image to a remote FTP server.
#
sub FileTransfer
{
  use Image::Magick;
  use URI::URL;
  use URI::Escape;
  use LWP::UserAgent;
  use LWP::MediaTypes qw(media_suffix);

  my($basename, $directory, $content, $filename, $format, $hostname,
     $image, $password, $path, $request, $response, $status, $url,
     $user_agent, $username);

  #
  # Read image.
  #
  SaveQueryState($q->param('SessionID'),'FileTransfer');
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  $basename=$q->param('Name');
  $format=$q->param('Magick');
  Error($status) if $#$image < 0;
  #
  # Construct FTP URL.
  #
  $action='output';
  $hostname=GetHostname($q->remote_host());
  $hostname=$q->param('Hostname') if $q->param('Hostname');
  $username='anonymous';
  $username=$q->param('Username') if $q->param('Username');
  $password="$username\@$hostname";
  $password=$q->param('Password') if $q->param('Password');
  $directory=uri_escape($q->param('Directory'),"^A-Za-z0-9") if ($q->param('Directory'));
  $filename="$basename.$format";
  $filename=uri_escape($q->param('Filename'),"^A-Za-z0-9") if $q->param('Filename');
  $url="ftp://$hostname/$filename";
  $url="ftp://$hostname/$directory/$filename" if $q->param('Directory');
  $q->delete('Password');
  $q->delete('Filename');
  SaveQueryState($q->param('SessionID'),'FileTransfer');
  #
  # Upload image.
  #
  $user_agent=new LWP::UserAgent;
  $user_agent->agent('MagickStudio/1.0 ' . $user_agent->agent);
  $user_agent->env_proxy if $ENV{'ftp_proxy'};
  $user_agent->timeout($Timeout);
  $request=HTTP::Request->new(PUT=>$url);
  $request->header('Content-Type','C');
  $request->authorization_basic($username,$password);
  $request->proxy_authorization_basic($username,$password);
  $image->Set(magick=>$format);
  $request->content($image->ImageToBlob());
  $response=$user_agent->request($request);
  Error(uri_unescape($url),$response->error_as_HTML) unless
    $response->is_success;
  Warning('Image uploaded',uri_unescape($url));
}

#
# Special Effects form.
#
sub FXForm
{
  my @OptionTypes =
  [
    'channel F(x) *',
    'charcoal drawing *',
    'clut',
    'color-matrix *',
    'connected components *',
    'convolve *',
    'distort *',
    'evaluate *',
    'forward Fourier transform',
    'function *',
    'F(x) *',
    'hald-clut',
    'implode *',
    'integral',
    'inverse Fourier transform',
    'morph *',
    'morphology *',
    'mosaic',
    'oil paint *',
    'sepia tone *',
    'shadow *',
    'sketch *',
    'solarize *',
    'stegano *',
    'stereo',
    'swirl *',
    'tint',
    'vignette *',
    'wave *',
    'wavelet denoise *'
  ];

  #
  # Display Effects form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To add special <a href="$DocumentDirectory/FX.html" target="help">effects</a> to your image, enter your effects parameter and method.  Note, only methods denoted with an asterisk require a parameter value.  Next, press <code>effect</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'effect'),
    "\n";
  print "<dt>Parameter:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Parameter',
    -size=>25,-value=>'60'), "</dd><br />\n";
  print "<dt>Choose from these special effects:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>3,-default=>'swirl *'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'effect'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>F/X Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Distort Type</th>\n";
  print "<th>Evaluate Type</th>\n";
  print "<th>Function Type</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @distorts=Image::Magick->QueryOption('distort');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'DistortType',
    -values=>[@distorts],-default=>'Arc'), "</td>\n";
  my @operators=Image::Magick->QueryOption('evaluate');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'EvaluateType',
    -values=>[@operators], -default=>'Sin'), "</td>\n";
  my @functions=Image::Magick->QueryOption('function');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'FunctionType',
    -values=>[@functions],-default=>'Sin'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Morphology Method</th>\n";
  print "<th>Virtual Pixel Method</th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @methods=Image::Magick->QueryOption('morphology');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'MorphologyMethod',
    -values=>[@methods]), "</td>\n";
  my @methods=Image::Magick->QueryOption('virtual-pixel');
  print '<td>', $q->popup_menu(-class=>'form-control',
    -name=>'VirtualPixelMethod',-values=>[@methods]), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Channel',
    -values=>[@channels],-default=>'Default'), "</td>\n";
  print "</tr>\n";
  print "</tr>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Background Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Fill Color</a></th>\n";
  print "</tr>\n";
  print "<tr><br />\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BackgroundColor',
    -value=>'black', -size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'FillColor',
    -value=>'white',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<dt> Miscellaneous options:</dt>\n";
  print '<dd>', $q->checkbox(-name=>'Repage',
    -checked=>'true',-label=>' reset page geometry.'), "</dd>\n";
  print '<dd>', $q->checkbox(-name=>'Clipboard',
    -label=>' use clipboard image as source for F(x).'),"</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# Return hostname from host address.
#
sub GetAddress
{
  use Socket;

  my($hostname) = @_;

  my $address = inet_ntoa(
    scalar gethostbyname( $hostname || 'localhost' )
  );
  $address;
}

#
# Return hostname from host address.
#
sub GetHostname
{
  my($hostname) = @_;

  my($address);

  $address=pack("C4",split(/\./,$hostname));
  $hostname=(gethostbyaddr($address,2))[0];
  $hostname;
}

#
# Return the average number of jobs in the run queue over the last minute.
#
sub GetLoadAverage
{
  my($load_average, $os);

  unless ($os = $^O)
  {
    require Config;
    $os=$Config::Config{'osname'};
  }
  $load_average=0;
  return if $os =~ /Win/i;
  if (!(-e "/proc/loadavg"))
    { $load_average=`uptime` =~ /average:\s+(\S+),/; }
  else
    {
      local(*DATA);

      open(DATA,"/proc/loadavg");
      $load_average=<DATA>;
      close(DATA);
    }
  $load_average+0.0;
}

#
# Generate the standard HTML title.
#
sub GetTitle
{
  use Image::Magick;

  my($image) = @_;

  my($height, $title, $width);

  if ($image)
    { ($width,$height)=$image->Get('columns','rows'); }
  else
    {
      my($format, $path, $size);

      $path=Untaint($q->param('Path'));
      $image=Image::Magick->new;
      ($width,$height,$size,$format)=$image->Ping("$path/MagickStudio.mpc");
    }
  $title=$q->param('Name') . '.' . $q->param('Magick') .  '  ' .  $width .
    'x' . $height;
  $title;
}

#
# Print the standard HTML header with the MagickStudio logo.
#
sub Header
{
  my($title, @attributes) = @_;

  my($cacheID, $magick, $name, $p, $path, $script, $sessionID, %tools,
     $tooltype, $url);

  #
  # Initialize tool types.
  #
  $tools{'Annotate'}='';
  $tools{'Colormap'}='';
  $tools{'Compare'}='';
  $tools{'Composite'}='';
  $tools{'Decorate'}='';
  $tools{'Download'}='';
  $tools{'Draw'}='';
  $tools{'Effects'}='';
  $tools{'Enhance'}='';
  $tools{'FX'}='';
  $tools{'Identify'}='';
  $tools{'Resize'}='';
  $tools{'Transform'}='';
  $tools{'Upload'}='';
  $tools{'View'}='';
  $q->param(-name=>'ToolType',-value=>'View') unless
    defined($q->param('ToolType'));
  $tooltype=$q->param('ToolType');
  $tools{$tooltype}.='active';
  #
  # Print the standard HTML header with the MagickStudio logo.
  #
  $header=1;
  $|=1;
  print $q->header(-charset=>'UTF-8',-expires=>$ExpireCache,@attributes), "\n";
  print $q->start_html(
    -meta=>{
      'charset'=>'utf-8', 
      'viewport'=>'width=device-width, initial-scale=1'
    },
    -head=>[
      "<link rel=\"icon\" href=\"$DocumentDirectory/images/wand.png\"/>",
      "<link rel=\"shortcut icon\" href=\"$DocumentDirectory/images/wand.ico\" type=\"image/x-icon\"/>"
    ],
    -title=>$title,-author=>$ContactInfo,-encoding=>'UTF-8',
    -style=>{-src=>"$DocumentDirectory/assets/magick-css.php"}), "\n";
  $script=$q->script_name;
  $cacheID=$q->param('CacheID');
  $sessionID=$q->param('SessionID');
  $path=$q->param('Path');
  $name=$q->param('Name');
  $magick=$q->param('Magick');
  $url=$q->script_name;
  $url.='?CacheID=' . $q->param('CacheID') if $q->param('CacheID');
  $url.=';SessionID=' . $q->param('SessionID') if $q->param('SessionID');
  $url.=';Path=' . $q->param('Path') if  $q->param('Path');
  $url.=';Name=' . $q->param('Name') if  $q->param('Name');
  $url.=';Magick=' . $q->param('Magick') if  $q->param('Magick');
  $url.=';Action=mogrify';
  print <<XXX;
  <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="$DocumentDirectory/"><img class="d-block" id="icon" alt="ImageMagick Online Studio" width="32" height="32" src="$DocumentDirectory/images/wand.ico"/></a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#magick-navbars" aria-controls="magick-navbars" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="magick-navbars">
      <form class="d-flex" action="$script">
        <input type="hidden" name="CacheID" value="$cacheID" />
        <input type="hidden" name="SessionID" value="$sessionID" />
        <input type="hidden" name="Path" value="$path" />
        <input type="hidden" name="Name" value="$name" />
        <input type="hidden" name="Magick" value="$magick" />
        <input type="hidden" name="ToolType" value="Upload" />
        <button class="btn btn-outline-success" type="submit">Upload</button>
      </form>
      <ul class="navbar-nav me-auto mb-2 mb-md-0">
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle  $tools{'View'} $tools{'Identify'}" href="#" id="view" data-bs-toggle="dropdown" aria-expanded="false">View</a>
          <ul class="dropdown-menu" aria-labelledby="nav-items-view">
            <li><a class="dropdown-item" href="$url;ToolType=View">View</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Identify">Identify</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Transform'} $tools{'Resize'}" href="#" id="transform" data-bs-toggle="dropdown" aria-expanded="false">Transform</a>
          <ul class="dropdown-menu" aria-labelledby="nav-items-transform">
            <li><a class="dropdown-item" href="$url;ToolType=Transform">Transform</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Resize">Resize</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Effects'} $tools{'F/X'} $tools{'Enhance'} $tools{'Colormap'}" href="#" id="effects" data-bs-toggle="dropdown" aria-expanded="false">Effects</a>
          <ul class="dropdown-menu" aria-labelledby="nav-items-effects">
            <li><a class="dropdown-item" href="$url;ToolType=Effects">Effects</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=FX">F/X</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Enhance">Enhance</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Colormap">Colormap</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Decorate'} $tools{'Annotate'} $tools{'Draw'}" href="#" id="decorate" data-bs-toggle="dropdown" aria-expanded="false">Decorate</a>
          <ul class="dropdown-menu" aria-labelledby="nav-items-decorate">
            <li><a class="dropdown-item" href="$url;ToolType=Decorate">Decorate</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Annotate">Annotate</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Draw">Draw</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Composite'} $tools{'Compare'}" href="#" id="composite" data-bs-toggle="dropdown" aria-expanded="false">Composite</a>
          <ul class="dropdown-menu" aria-labelledby="nav-items-composite">
            <li><a class="dropdown-item" href="$url;ToolType=Composite">Composite</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Compare">Compare</a></li>
          </ul>
        </li>
      </ul>
      <form class="d-flex" action="$script">
        <input type="hidden" name="Action" value="mogrify" />
        <input type="hidden" name="CacheID" value="$cacheID" />
        <input type="hidden" name="SessionID" value="$sessionID" />
        <input type="hidden" name="Path" value="$path" />
        <input type="hidden" name="Name" value="$name" />
        <input type="hidden" name="Magick" value="$magick" />
        <input type="hidden" name="ToolType" value="Download" />
        <button class="btn btn-outline-success" type="submit">Download</button>
      </form>
    </div>
  </div>
  </nav>
<div class="container">
  <script async="async" src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
  <ins class="adsbygoogle"
    style="display:block"
    data-ad-client="ca-pub-3129977114552745"
    data-ad-slot="6345125851"
    data-full-width-responsive="true"
    data-ad-format="horizontal"></ins>
  <script>
    (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
<main class="container">
	<div class="magick-template">
XXX
  ;
  print <<XXX;
XXX
  ;
}

#
# Identify an image.
#
sub Identify
{
  use Image::Magick;

  my($class, $filename, $format, $height, $image, $images, $matte,
    $magick, $path, $status, $width, $x);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $images=Image::Magick->new(precision=>6);
  $status=$images->Read("$path/MagickStudio.mpc");
  Error($status) if $#$images < 0;
  $magick=$q->param('Magick');
  $filename=$q->param('Name') . '.' . $magick;
  $images->Set(filename=>$filename,magick=>$magick);
  #
  # Display image on web page.
  #
  Header(GetTitle($images));
  print <<XXX;
<p class="lead magick-description">Here is a detailed description of your image, <code>$filename</code>:</p>
XXX
  ;
  print "<ul><pre class=\"pre-scrollable\"><samp>";
  $images->Identify();
  print "</samp></pre></ul>\n";
  Trailer(1);
}

#
# Choose the appropriate Web page based on the ToolType parameter.
#
sub Mogrify
{
  my ($function, $tooltype, %Tools);

  %Tools=
  (
    'Upload'=>\&UploadForm,
    'View'=>\&ViewForm,
    'Identify'=>\&Identify,
    'Download'=>\&DownloadForm,
    'Colormap'=>\&ColormapForm,
    'Resize'=>\&ResizeForm,
    'Transform'=>\&TransformForm,
    'Enhance'=>\&EnhanceForm,
    'Effects'=>\&EffectsForm,
    'FX'=>\&FXForm,
    'Decorate'=>\&DecorateForm,
    'Annotate'=>\&AnnotateForm,
    'Draw'=>\&DrawForm,
    'Composite'=>\&CompositeForm,
    'Compare'=>\&CompareForm,
    'Comment'=>\&CommentForm
  );

  $tooltype=$q->param('ToolType');
  View() unless defined($tooltype);
  Error('Unable to view image','no path is defined') unless $q->param('Path');
  RestoreQueryState($q->param('SessionID'),$q->param('Path'),$tooltype);
  $function=$Tools{$tooltype};
  &$function() if defined($function);
  Error('Request failed due to malformed query');
}

#
# Resize image.
#
sub Resize
{
  use Image::Magick;

  my($blur, $filter, $geometry, $image, $montage, $path, $status, $support,
    $value);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Resize image.
  #
  $image->Set(gravity=>$q->param('Gravity'));
  $q->param('Geometry') =~ /(\d+)\D*(\d*)/;
  Error('Image area exceeds maximum allowable') if $1 && $2 &&
    (($1*$2) > (1024*$MaxImageArea));
  Error('Image area exceeds maximum allowable') if $1 && !$2 &&
    (($1*$1) > (1024*$MaxImageArea));
  $geometry='100%';
  $geometry=$q->param('Geometry') if $q->param('Geometry');
  $filter='Undefined';
  $filter=$q->param('FilterType') if $q->param('FilterType');
  $support='0.0';
  $support=$q->param('SupportFactor') if $q->param('SupportFactor');
  $blur='1.0';
  $blur=$q->param('BlurFactor') if $q->param('BlurFactor');
  $image->AdaptiveResize(geometry=>$geometry,filter=>$filter,blur=>$blur) if
    $q->param('Algorithm') eq 'adaptive resize *';
  $image->LiquidRescale(geometry=>$geometry) if
    $q->param('Algorithm') eq 'liquid rescale *';
  $image->Resize(geometry=>$geometry,filter=>$filter,blur=>$blur) if
    $q->param('Algorithm') eq 'resize *';
  $image->Scale($geometry) if $q->param('Algorithm') eq 'scale *';
  $image->Sample($geometry) if $q->param('Algorithm') eq 'sample *';
  $image->Magnify() if $q->param('Algorithm') eq 'double size';
  $image->Minify() if $q->param('Algorithm') eq 'half size';
  $image->Extent(geometry=>$geometry,background=>$q->param('BackgroundColor'))
    if $q->param('Algorithm') eq 'extent *';
  $image->Resample(density=>$geometry,filter=>$filter,blur=>$blur) if
    $q->param('Algorithm') eq 'resample *';
  $image->Thumbnail($geometry) if $q->param('Algorithm') eq 'thumbnail *';
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Resize image form.
#
sub ResizeForm
{
  use Image::Magick;

  my($height, $image, @OptionTypes, $path, $width);

  @OptionTypes=
  [
    'resize *',
    'adaptive resize *',
    'double size',
    'extent *',
    'half size',
    'liquid rescale *',
    'resample *',
    'sample *',
    'scale *',
    'thumbnail *'
  ];

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  ($width,$height)=$image->Ping("$path/MagickStudio.mpc");
  $q->delete('Geometry');
  #
  # Display Resize form.
  #
  Header(GetTitle($image));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Resize.html" target="help">resize</a> your image, specify the desired size and scaling method.  Note, only methods denoted with an asterisk require a parameter value.  Next, press <code>resize</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'resize'),
    "\n";
  print "<dt>Image size:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Geometry',
    -size=>25,-value=>"$width" . 'x' . "$height"), "</dd><br />\n";
  print "<dt>Choose from these scaling methods:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Algorithm',-values=>@OptionTypes,
    -columns=>3), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'resize'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Resize Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Filter</th>\n";
  print "<th>Support</th>\n";
  print "<th>Blur</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('filter');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Primitive',
    -values=>[@types]), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SupportFactor',
    -size=>25,-value=>'0.0'), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BlurFactor',
    -size=>25,-value=>'1.0'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<dd><table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Gravity</th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">",
    "Background Color</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('gravity');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Gravity',
    -values=>[@types]), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BackgroundColor',
    -value=>'none', -size=>25), "</td>\n";
  print "</tr>\n";
  print '</table></dd><br />';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br />
XXX
  ;
  Trailer(1);
}

#
# Restore query state from a file.
#
sub RestoreQueryState
{
  no strict 'subs';

  my($session, $path, $tooltype) = @_;

  my($filename);

  local(*DATA);

  $filename=Untaint($DocumentRoot . $DocumentDirectory .
    "/session_info/$session.$tooltype");
  open(DATA,$filename) || return;
  $q=CGI->new(DATA);
  close(DATA);
  $q->param(-name=>'Path',-value=>$path);
}

#
# Save query state to a file.
#
sub SaveQueryState
{
  no strict 'subs';

  my($session, $tooltype) = @_;

  my($filename, $path, $remote_host);

  local(*DATA);

  $path=$DocumentRoot . $DocumentDirectory . "/session_info";
  $filename=Untaint("$path/$session.$tooltype");
  open(DATA,">$filename") || Error('Unable to view image',$filename);
  $q->save(DATA);
  print DATA "pid: $$\n";
  print DATA "image locator: ", $q->param('File'), "\n" if $q->param('File');
  print DATA "image locator: ", $q->param('URL'), "\n" if $q->param('URL');
  $remote_host='localhost';
  $remote_host=$q->remote_host() if $q->remote_host();
  print DATA "server name: ", $q->server_name(), "\n" if $q->server_name();
  print DATA "remote host: ", GetHostname($remote_host), "\n";
  print DATA "remote addr: ", $q->remote_addr(), "\n" if $q->remote_addr();
  print DATA "remote ident: ", $q->remote_ident(), "\n" if $q->remote_ident();
  print DATA "remote user: ", $q->remote_user(), "\n" if $q->remote_user();
  print DATA "user name: ", $q->user_name(), "\n" if  $q->user_name();
  print DATA "user agent: ", $q->user_agent(), "\n" if $q->user_agent();
  print DATA "time stamp: ", scalar(localtime), "\n";
  close(DATA);
}

#
# Print the standard HTML trailer.
#
sub Trailer
{
  my($display) = @_;

  my($home, $load_average, $url);

  print <<XXX;
  </div>
</main>
XXX
  ;
  #
  # Display home and comment icon.
  #
  $url=$q->script_name;
  $load_average=GetLoadAverage();
  $home="$DocumentDirectory/images/home-go.png";
  $home="$DocumentDirectory/images/home-caution.png"
    if $load_average >= ($LoadAverageThreshold/3);
  $home="$DocumentDirectory/images/home-stop.png"
    if $load_average >= (2*$LoadAverageThreshold/3);
  print <<XXX;
  <footer class="magick-footer">
  <div class="container-fluid">
XXX
  ;
  if ($display)
    {
      my($filename, $height, $image, $path, $url, $width);

      #
      # Display image and clipboard icon.
      #
      $image=Image::Magick->new;
      $path="";
      $path=Untaint($q->param('Path')) if $q->param('Path');
      $filename="$path/MagickStudio.gif";
      if (-e $filename)
        {
          ($width,$height)=$image->Ping("$filename" . '[0]');
          $url=substr($path,length($DocumentRoot));
          print "<img alt=\"image icon\" src=\"$url/MagickStudio.gif\" ",
            "border=\"0\" width=\"$width\" height=\"$height\" ",
            "class=\"img-thumbnail img-fluid float-start\"/>\n";
        }
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.gif';
      if (-e $filename)
        {
          ($width,$height)=$image->Ping("$filename" . '[0]');
          print "<img alt=\"clipboard icon\" src=\"$DocumentDirectory/",
            "clipboard/", $q->param('SessionID'), ".gif\" border=\"0\" ",
            "width=\"$width\" height=\"$height\" ",
            "class=\"img-thumbnail img-fluid float-start\"/>\n";
        }
    }
  print <<XXX;
    <div class="nav-link">
      <p><a href="#">Back to top</a> •
         <a href="https://github.com/ImageMagick/ImageMagick/discussions">Community</a> •
         <a href="https://github.com/sponsors/ImageMagick?o=esb">Donate</a></p>
    </div>
XXX
  print <<XXX;
    <p><small>&copy; 1999-2021 ImageMagick Studio LLC</small></p>
  </div>
  </footer>
  <!-- Javascript assets -->
  <script src="$DocumentDirectory/assets/magick-js.php"></script>
XXX
  ;
  if ($Debug)
    {
      my($name);

      #
      # Display debugging information for an administrator.
      #
      print "<center><h3>CGI State Information</h3></center>\n";
      print "Script:\n";
      print '<dd>', $0, "<br />\n";
      print "Action:\n";
      print '<dd>', $action, "<br />\n";
      print "Time:\n";
      print '<dd>', time-$timer, "s<br />\n";
      print "Query state:\n";
      print '<dd>', $q->query_string, "<br />\n";
      print $q->Dump;
      print "<br />\n";
      print "Environment state:\n";
      print "<ul>\n";
      print "<li><code>SponsorURL</code>: ", $SponsorURL, "<br />\n";
      print "<li><code>SponsorIcon</code>: ", $SponsorIcon, "<br />\n";
      print "<li><code>accept</code>: ", $q->Accept(), "<br />\n";
      print "<li><code>auth type</code>: ", $q->auth_type(), "<br />\n";
      print "<li><code>raw cookie</code>: ", $q->raw_cookie(), "<br />\n";
      print "<li><code>path info</code>: ", $q->path_info(), "<br />\n";
      print "<li><code>path translated</code>: ", $q->path_translated(), "<br />\n";
      print "<li><code>referer</code>: ", $q->referer(), "<br />\n";
      print "<li><code>local addr</code>: ", GetAddress($q->virtual_host()), "<br />\n";
      print "<li><code>remote addr</code>: ", $q->remote_addr(), "<br />\n";
      print "<li><code>remote ident</code>: ", $q->remote_ident(), "<br />\n";
      print "<li><code>remote host</code>: ", GetHostname($q->remote_host()), "<br />\n";
      print "<li><code>remote user</code>: ", $q->remote_user(), "<br />\n";
      print "<li><code>request method</code>: ", $q->request_method(), "<br />\n";
      print "<li><code>script name</code>: ", $q->script_name(), "<br />\n";
      print "<li><code>server name</code>: ", $q->server_name(), "<br />\n";
      print "<li><code>server software</code>: ", $q->server_software(), "<br />\n";
      print "<li><code>server port</code>: ", $q->server_port(), "<br />\n";
      print "<li><code>temporary directory</code>: ", $ENV{TMPDIR}, "<br />\n";
      print "<li><code>user agent</code>: ", $q->user_agent(), "<br />\n";
      print "<li><code>user name</code>: ", $q->user_name(), "<br />\n";
      print "<li><code>virtual host</code>: ", $q->virtual_host(), "<br />\n";
      print "<li><code>environment</code>: ", $q->http(), "<br />\n";
      print "<li><code>time stamp</code>: ", scalar(localtime), "<br />\n";
      print "</ul>\n";
    }
  print $q->end_html;
  exit;
}

#
# Transform image.
#
sub Transform
{
  use Image::Magick;

  my($color, $image, $parameter, $path, $status);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Transform image.
  #
  $parameter=$q->param('Parameter');
  $image->Set(fuzz=>$q->param('Fuzz')) if $q->param('Fuzz');
  $image->Set(background=>$q->param('BackgroundColor'));
  $image->Set(gravity=>$q->param('Gravity'));
  $image->AffineTransform([split(/[ ,]+/,$parameter)]) if
    $q->param('Option') eq 'affine *';
  $image->AutoOrient() if $q->param('Option') eq 'auto-orient';
  $image->Trim() if $q->param('Option') eq 'trim';
  $image->Crop("$parameter") if $q->param('Option') eq 'crop *';
  $image->Chop("$parameter") if $q->param('Option') eq 'chop *';
  $image=$image->Coalesce() if $q->param('Option') eq 'coalesce';
  $image->Colorspace($q->param('Colorspace')) if
    $q->param('Option') eq 'colorspace';
  $image->Deconstruct() if $q->param('Option') eq 'deconstruct';
  $image->Deskew($parameter) if $q->param('Option') eq 'deskew';
  $image=$image->Flatten() if $q->param('Option') eq 'flatten';
  $image->Flop() if $q->param('Option') eq 'flop';
  $image->Flip() if $q->param('Option') eq 'flip';
  $image=$image->Layers(method=>$q->param('LayerMethod')) if
    $q->param('Option') eq 'layers';
  $image->Rotate(90) if $q->param('Option') eq 'rotate right';
  $image->Rotate(-90) if $q->param('Option') eq 'rotate left';
  $color='none';
  $color=$q->param('BackgroundColor') if $q->param('BackgroundColor');
  $image->Rotate(degrees=>$parameter,background=>$color) if
    $q->param('Option') eq 'rotate *';
  $image->Shave("$parameter") if $q->param('Option') eq 'shave *';
  $image->Shear("$parameter") if $q->param('Option') eq 'shear *';
  $image->Splice("$parameter") if $q->param('Option') eq 'splice *';
  $image->Roll("$parameter") if $q->param('Option') eq 'roll *';
  $image->Set(page=>'0x0+0+0') if $q->param('Repage') eq 'on';
  $image->Transpose() if $q->param('Option') eq 'transpose';
  $image->Transverse() if $q->param('Option') eq 'transverse';
  $image->UniqueColors() if $q->param('Option') eq 'unique colors';
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Transform image form.
#
sub TransformForm
{
  my @OptionTypes=
  [
    'affine *',
    'auto-orient',
    'chop *',
    'colorspace',
    'coalesce',
    'crop *',
    'deconstruct',
    'deskew',
    'flatten',
    'flip',
    'flop',
    'layers',
    'roll *',
    'rotate *',
    'rotate left',
    'rotate right',
    'shave *',
    'shear *',
    'splice *',
    'transpose',
    'transverse',
    'trim',
    'unique colors'
  ];

  #
  # Display Transform form.
  #
  Header(GetTitle(undef));
  print <<XXX;
<p class="lead magick-description">To <a href="$DocumentDirectory/Transform.html" target="help">transform</a> your image, enter your transform parameter and method.  Note, only methods denoted with an asterisk require a parameter value.  Next, press <code>transform</code> to continue.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'resize'),
    "\n";
  print "<dt>Parameter:</dt>\n";
  print '<dd>', $q->textfield(-class=>'form-control',-name=>'Parameter',
    -size=>25), "</dd><br />\n";
  print "<dt>Choose from these transforms:</dt>\n";
  print '<dd>', $q->radio_group(-name=>'Option',-values=>@OptionTypes,
    -columns=>3,-default=>'trim'), "</dd><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'transform'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.<br /><br />\n";
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Transform Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\">Fuzz</a></th>\n";
  print "<th>Gravity</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,
    -value=>'0%'), "</td>\n";
  my @types=Image::Magick->QueryOption('gravity');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Gravity',
    -values=>[@types]), "</td>\n";
  print "</tr>\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Colorspace.html\" target=\"help\">Colorspace</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('colorspace');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Colorspace',
    -values=>[@types],-default=>'sRGB'), "</td>\n";
  print "<tr>\n";
  print '</table><br />';
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th>Layer Method</th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Background Color</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  my @types=Image::Magick->QueryOption('layers');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'LayerMethod',
    -values=>[@types],-default=>'Optimize'), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BackgroundColor',
    -value=>'none',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<dt> Miscellaneous options:</dt>\n";
  print '<dd>', $q->checkbox(-name=>'Repage',
    -checked=>'true',-label=>' reset page geometry.'), "</dd>\n";
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# Untaint Perl variable.
#
sub Untaint
{
  my($filename) = @_;

  if ($filename =~ /\&\;\`\'\"\|*?\~\<\>\^()\[\]\{\}\$\n\r/)
    {
      $filename=~s/\&\;\`\'\"\|*?\~\<\>\^()\[\]\{\}\$\n\r/\?/g;
      Error('Your filename contains prohibited characters',$filename);
    }
  $filename;
}

#
# Upload image.
#
sub Upload
{
  no strict 'refs';
  no strict 'subs';

  use Image::Magick;
  use LWP::Simple;
  use File::Basename;
  use File::Copy;
  use Digest::SHA3;

  my(@attributes, $basename, $digest, $extent, @extents, $filename, $format,
     $i, $image, $magick, $path, $session, $status, $scene);

  #
  # Expire files.
  #
  $path=$DocumentRoot . $DocumentDirectory;
  ExpireFiles("$path/workarea",$ExpireThreshold);
  ExpireFiles("$path/clipboard",$ExpireThreshold);
  ExpireFiles("$path/tmp",$ExpireThreshold);
  ExpireFiles("$path/session_info",7*$ExpireThreshold);
  ExpireFiles("$path/comments",14*$ExpireThreshold);
  #
  # Read image.
  #
  Error('You must specify either an image filename or URL') unless
    ($q->param('File') || $q->param('URL') || $q->param('Meta'));
  CreateWorkDirectory(undef);
  $path=$q->param('Path');
  $format='';
  $format=$q->param('Format') . ':'
    if ($q->param('Format') && ($q->param('Format') ne 'Implicit'));
  $scene='';
  $scene='[' . $q->param('Scene') . ']' if $q->param('Scene');
  $image=Image::Magick->new;
  $image->Set(font=>$DefaultFont);
  $image->Set(density=>$q->param('Density')) if $q->param('Density');
  $image->Set(size=>$q->param('SizeGeometry')) if $q->param('SizeGeometry');
  if ($q->param('File'))
    {
      #
      # Copy data file to workarea.
      #
      $filename=Untaint($q->param('File'));
      copy($q->upload('File'),'MagickStudio.dat') ||
        copy(\*$filename,'MagickStudio.dat') ||
          getstore($filename,'MagickStudio.dat');
      if (-z 'MagickStudio.dat')
        {
          $q->param('SizeGeometry')=~/(\d+)\D*(\d*)/;
          Error('Image area exceeds maximum allowable') if $1 && $2 &&
            (($1*$2) > (1024*$MaxImageArea));
          Error('Image area exceeds maximum allowable') if $1 && !$2 &&
            (($1*$1) > (1024*$MaxImageArea));
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc' if $filename eq 'clipboard:';
          $format=$q->param('Format') . ':' if $q->param('Format');
          $status=$image->Read("$format$filename$scene");
          Error($status) if $#$image < 0;
          $status=$image->Write('MagickStudio.dat');
          Error($status) if "$status";
          $format='';
        }
    }
  else
    {
      if ($q->param('URL'))
        {
          $filename=Untaint($q->param('URL'));
          if (!($filename =~ /\/$/))
            {
              #
              # Copy HTTP content to MagickStudio.dat.
              #
              getstore($filename,'MagickStudio.dat');
              if ((-f 'MagickStudio.dat') && (-s 'MagickStudio.dat'))
                {
                  if (($filename =~ /.html$/) || ($filename =~ /.htm$/))
                    {
                      #
                      # Convert HTML content to Postscript.
                      #
                      @extents=$image->Ping("$filename");
                      $extent=0;
                      for ($i=0; $i < $#extents; $i+=4)
                        { $extent+=$extents[$i]*$extents[$i+1]; }
                      Error('Image extents exceeds maximum allowable') if
                        $extent && ($extent > (1024*$MaxImageExtent));
                      $status=$image->Read($filename);
                      Error($status) if $#$image < 0;
                      $status=$image->Write('MagickStudio.dat');
                      Error($status) if "$status";
                    }
                }
            }
          else
            {
              #
              # Copy all images in HTTP directory to MagickStudio.dat.
              #
              FetchImages($filename,undef,0);
              @extents=$image->Ping("*");
              $extent=0;
              for ($i=0; $i < $#extents; $i+=4)
                { $extent+=$extents[$i]*$extents[$i+1]; }
              Error('Image extents exceeds maximum allowable') if $extent &&
                ($extent > (1024*$MaxImageExtent));
              $status=$image->Read("*");
              Error($status) if $#$image < 0;
              $status=$image->Write('MagickStudio.dat');
              Error($status) if "$status";
              chop($filename);
            }
        }
      else
        {
          if ($q->param('Meta') && ($q->param('Format') ne 'Implicit'))
            {
              $filename=Untaint($q->param('Meta'));
              $q->param('SizeGeometry') =~ /(\d+)\D*(\d*)/;
              Error('Image area exceeds maximum allowable') if $1 && $2 &&
                (($1*$2) > (1024*$MaxImageArea));
              Error('Image area exceeds maximum allowable') if $1 && !$2 &&
                (($1*$1) > (1024*$MaxImageArea));
              $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
                $q->param('SessionID') . '.mpc' if $filename eq 'clipboard:';
              $format=$q->param('Format') . ':' if $q->param('Format');
              $status=$image->Read("$format$filename$scene");
              Error($status) if $#$image < 0;
              $image->Set(magick=>'mpc');
              $status=$image->Write('MagickStudio.dat');
              Error($status) if "$status";
              $image->Set(magick=>'mpc');
              $format='';
            }
          }
    }
  $magick=$image->Get('magick');
  Error('Unable to read image file',$filename)
    unless (-f 'MagickStudio.dat') && (-s 'MagickStudio.dat');
  Error('Image size exceeds maximum allowable',$filename)
    unless (-s 'MagickStudio.dat') < (1024*$MaxFilesize);
  #
  # Read image.
  #
  $image=Image::Magick->new;
  $image->Set(font=>$DefaultFont);
  $image->Set(density=>$q->param('Density')) if $q->param('Density');
  $image->Set(size=>$q->param('SizeGeometry')) if $q->param('SizeGeometry');
  @extents=$image->Ping("$format$path/MagickStudio.dat$scene");
  $extent=0;
  for ($i=0; $i < $#extents; $i+=4) { $extent+=$extents[$i]*$extents[$i+1]; }
  Error('Image extents exceeds maximum allowable') if $extent &&
    ($extent > (1024*$MaxImageExtent));
  $image=Image::Magick->new;
  $image->Set(density=>$q->param('Density')) if $q->param('Density');
  $status=$image->Read("$format$path/MagickStudio.dat$scene");
  Error($status) if $#$image < 0;
  $magick=$image->Get('magick') if $image->Get('magick') ne 'MPC';
  unlink('MagickStudio.dat');
  if (length($q->param('Passphrase')) > 0)
    {
      my($passphrase);

      $passphrase=$q->param('Passphrase');
      $image->Decipher($passphrase);
    }
  if (defined($q->param('Channel')))
    {
      my($channel);

      $channel=$q->param('Channel');
      $image->Separate($channel) unless $channel eq 'All';
    }
  $basename=$filename;
  $filename=~/^((?:.*[:\\\/])?)(.*)(\..*)/s;
  $basename=$2 if $2;
  $basename=~s/ //g;
  $basename=~s/#//g;
  $q->param(-name=>'Name',-value=>$basename);
  $magick=~tr/A-Z/a-z/;
  $q->param(-name=>'Magick',-value=>$magick);
  $digest=Digest::SHA3->new(512);
  $digest->add($HashDigestSalt,$image->Get('signature'),$filename,
    $q->remote_addr(),time(),{},rand(),$$);
  $session=$digest->hexdigest;
  if (defined($q->param('SessionID')))
    {
      my($clipboard, $filename);

      #
      # Paste file to clipboard.
      #
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.mpc';
      $clipboard=Image::Magick->new;
      $status=$clipboard->Read($filename);
      push(@$image,@$clipboard) if defined($q->param('Append'));
      if ($#$clipboard >= 0)
        {
          $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $session;
          $status=$clipboard->Write(filename=>"$filename.mpc");
          Error($status) if "$status";
          $clipboard=$clipboard->Coalesce();
          $clipboard->Resize($IconSize);
          $status=$clipboard->Write("$filename.gif");
          Error($status) if "$status";
        }
    }
  $q->param(-name=>'SessionID',-value=>$session);
  SaveQueryState($session,'Upload');
  $q->delete('File');
  $q->delete('URL');
  #
  # Write image.
  #
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Get the name of a file to use as input by the MagickStudio tools.
#
sub UploadForm
{
  my($action, $filename, @UploadTypes, $url, $version, $load_average);

  #
  # Define input image formats.
  #
  @UploadTypes=
  (
    'Implicit',
    'caption',
    'cmyk',
    'fax',
    'gradient',
    'granite',
    'gray',
    'hald',
    'label',
    'mono',
    'netscape',
    'pango',
    'pattern',
    'plasma',
    'rgb',
    'rgba',
    'text',
    'uyvy',
    'xc',
    'yuv'
  );

  #
  # Display input image form.
  #
  $load_average=GetLoadAverage();
  if ($load_average > $LoadAverageThreshold)
    {
      print $q->redirect($RedirectURL);
      exit;
    }
  $url=$q->script_name();
  $q->delete('ToolType');
  $q->param(-name=>'ToolType',-value=>'Upload');
  Header("Magick Online Studio");
  print <<XXX;
<br />
<p class="lead magick-description">To convert, edit, or compose your image online, press <code>Choose File</code> to browse and select your image file or enter the <a href="$DocumentDirectory/URL.html" target="help">URL</a> of your image.  Next, set any of the optional parameters below.  Finally, press <code>view</code> to continue.</p>
XXX
  ;
  $version=Image::Magick->VERSION;
  $version=Image::Magick::Q8->VERSION if !defined($version);
  $version=Image::Magick::Q8HDRI->VERSION if !defined($version);
  $version=Image::Magick::Q16->VERSION if !defined($version);
  $version=Image::Magick::Q16HDRI->VERSION if !defined($version);
  $version=Image::Magick::Q32->VERSION if !defined($version);
  $version=Image::Magick::Q32HDRI->VERSION if !defined($version);
  $action=$url . "?CacheID=" . $q->param('CacheID') .  ";Action=view";
  print $q->start_multipart_form(-action=>$action,-class=>'form-horizontal');
  print $q->hidden(-name=>'SessionID'), "\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<td><a href=\"$DocumentDirectory/Filename.html\" target=\"help\">Filename</a>:</td>\n";
  print '<td>', $q->filefield(-name=>'File',-size=>50,-maxlength=>1024), "</td>\n";
  print "</tr>\n";
  print "<tr>\n";
  print "<td><a href=\"$DocumentDirectory/URL.html\" target=\"help\">URL</a>:</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'URL',-size=>50),
    "</td>\n";
  $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
    $q->param('SessionID')  . '.mpc';
  if ((-e $filename) && defined($q->param('SessionID')))
    {
      print '<td>', $q->checkbox(-name=>'Append',
        -label=>' append to clipboard image.'), "</td>\n";
    }
  print "</tr>\n";
  print "</table><br />\n";
  print 'Press to ', $q->submit(-name=>'Action',-class=>'btn btn-primary',
    -value=>'view'), ' your image or ', $q->reset(-name=>'reset',
    -class=>'btn btn-warning'), " the form.\n";
  print <<XXX;
<br /> <br />
An example <a href="$url?URL=$ExampleImage;Action=view"> image</a> is available to help you get familiar with <code>Magick Online Studio</code>, version $version.
<br /> <br />
<fieldset>
<legend>Privacy Notice</legend>
<p class="text-warning">Your privacy is protected as long as you use this service in a lawful manner.  All uploaded images are temporarily stored on our local disks for processing and they are <var>automagically</var> removed within a few hours.  Your images cannot be viewed or copied by anyone other than yourself.  We have security precautions in place to prevent others from accessing your images.</p>
</fieldset>
<br />
<fieldset>
<legend>Liability Notice</legend>
<p class="text-warning">By using this service, you agree not to hold ImageMagick Studio LLC liable for any data loss, subsequent damages, or privacy issues resulting from the use of this service.</p>
</fieldset>
<br />
XXX
  ;
  print "<fieldset>\n";
  print "<legend>Upload Properties</legend>\n";
  print <<XXX;
<p>You rarely need to set these parameters.  The scene specification is useful when you want to view only a few frames from a multi-frame image.  The remaining options are only necessary for raw image formats such as RGB or GRAY.</p>
<dl><dd>
XXX
  ;
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Size.html\" target=\"help\">Size</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Format.html\" target=\"help\">Format</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'SizeGeometry',
    -size=>25,-value=>'320x240'), "</td>\n";
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Format',
    -values=>[@UploadTypes]), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Meta.html\" target=\"help\">Meta</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Interlace.html\" target=\"help\">Interlace</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Meta',-size=>25,
    -value=>'white'), "</td>\n";
  my @types=Image::Magick->QueryOption('interlace');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Interlace',
    -values=>[@types],-default=>'None'), "</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Scene.html\" target=\"help\">Scene</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Channel.html\" target=\"help\">Channel</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Scene',
    -size=>25), "</td>\n";
  my @channels=Image::Magick->QueryOption('channel');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Channel',
    -values=>[@channels],-default=>'All'), "</td>\n";
  print "</tr>\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Passphrase.html\" target=\"help\">Passphrase</a></th>\n";
  print "<th>Density</th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Passphrase',
    -size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Density',
    -size=>8,-value=>90), "</td>\n";
  print "</tr>\n";
  print '</table>';
  print '</dd></dl>';
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
XXX
  ;
  Trailer(1);
}

#
# View image.
#
sub View
{
  use Image::Magick;

  my($basename, $bordercolor, $extent, @extents, $fill, $i, $image, $method,
     $path, $points, $primitive, $status);

  #
  # Read image.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  $image=Image::Magick->new;
  @extents=$image->Ping("$path/MagickStudio.mpc");
  $extent=0;
  for ($i=0; $i < $#extents; $i+=4) { $extent+=$extents[$i]*$extents[$i+1]; }
  Error('Image extents exceeds maximum allowable') if $extent &&
    ($extent > (1024*$MaxImageExtent));
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  if ($q->param('Primitive') ne 'None')
    {
      #
      # Paint image.
      #
      $image->Set(fuzz=>$q->param('Fuzz')) if $q->param('Fuzz');
      $primitive=$q->param('Primitive');
      $basename=$q->param('Name');
      my $width=$image->Get('columns');
      my $height=$image->Get('rows');
      my $x=$q->param("$basename.x");
      my $y=$q->param("$basename.y");
      my $page=$image->Get('page');
      if ($page =~ /(\d+\.*\d*)x(\d+\.*\d*)\+(\d+\.*\d*)\+(\d+\.*\d*)/)
        {
          $width=$1;
          $height=$2;
          $x-=$3;
          $y-=$4;
        }
      $points=$x . ',' . $y;
      $fill='none';
      $fill=$q->param('Color') if $q->param('Color');
      if ($fill eq '@clipboard')
        {
          $fill='@' . $DocumentRoot . $DocumentDirectory . '/clipboard/' .
            $q->param('SessionID') . '.mpc';
        }
      $bordercolor='none';
      $bordercolor=$q->param('BorderColor') if $q->param('BorderColor');
      $method=$q->param('Method');
      $image->Draw(primitive=>$primitive,points=>$points,fill=>$fill,
        bordercolor=>$bordercolor,method=>$method);
    }
  #
  # Write image.
  #
  CreateWorkDirectory(1);
  Header(GetTitle($image));
  $status=$image->Write(filename=>'MagickStudio.mpc');
  Error($status) if "$status";
  ViewForm($image);
}

#
# Display View form.
#
sub ViewForm
{
  use Image::Magick;

  my($image) = @_;

  my($basename, $coalesce, $filesize, $format, $height, $icon, %mimes, $path,
    @PrimitiveTypes, $status, $url, $width);

  @PrimitiveTypes=
  (
    'None',
    'Color',
    'Matte'
  );

  #
  # Ensure image resources are within bounds.
  #
  $path=Untaint($q->param('Path'));
  chdir($path) || Error('Your image has expired',$path);
  if (!$image)
    {
      #
      # Read image.
      #
      $image=Image::Magick->new;
      $status=$image->Read("$path/MagickStudio.mpc");
      Error($status) if $#$image < 0;
      Header(GetTitle($image));
    }
  #
  # Convert the image to viewable format.
  #
  $icon=$image->Coalesce();
  $icon->Resize($IconSize);
  $status=$icon->Write(filename=>'MagickStudio.gif');
  Error($status) if "$status";
  $basename=$q->param('Name');
  $format='png';
  $coalesce=$image->Coalesce();
  if ($#$coalesce > 0)
    {
      $format='gif';
      $coalesce->Set(loop=>0,delay=>800) if $coalesce->Get('iterations') == 1;
    }
  $coalesce->Set(interlace=>'none');
  $status=$coalesce->Write("$basename.$format");
  Error($status) if "$status";
  #
  # Display View form.
  #
  ($width,$height)=$coalesce->Get('width','height');
  $url=substr($path,length($DocumentRoot));
  print <<XXX;
<p class="lead magick-description">Here is your image.  Click on a tab above to interactively resize, rotate, sharpen, color reduce, or add special effects to your image and save the completed work in the same or differing image format.  Press <code>Back</code> to undo your last image transformation.  For more information, see <a href="https://imagemagick.org/">ImageMagick</a>.</p>
<p>You can optionally <a href="$DocumentDirectory/Paint.html" target="help">paint</a> on your image.  Set any optional attributes below and click on the appropriate location within your image.</p>
XXX
  ;
  print $q->start_form(-class=>'form-horizontal');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'view'),
    "\n";
  print $q->image_button(-class=>'img-fluid mx-auto d-block',-name=>$basename,
    -src=>"$url/$basename.$format",-border=>1,-width=>$width,-height=>$height,
    -style=>"cursor:crosshair",-cursor), "<br />\n";
  if (defined($q->param("$basename.x")) || defined($q->param("$basename.y")))
    {
      my $width=$coalesce->Get('columns');
      my $height=$coalesce->Get('rows');
      my $x=$q->param("$basename.x");
      my $y=$q->param("$basename.y");
      print "<ul><pre class=\"highlight\"><samp>$x,$y: ";
      my $page=$coalesce->Get('page');
      if ($page =~ /(\d+\.*\d*)x(\d+\.*\d*)\+(\d+\.*\d*)\+(\d+\.*\d*)/)
        {
          $width=$1;
          $height=$2;
          $x-=$3;
          $y-=$4;
        }
      my $color=$coalesce->Get("pixel[$x,$y]");
      my ($red,$green,$blue,$alpha)=split(/[ ,]+/,$color);
      $red=100.0*$red/(Image::Magick->QuantumRange);
      $green=100.0*$green/(Image::Magick->QuantumRange);
      $blue=100.0*$blue/(Image::Magick->QuantumRange);
      $alpha=1.0-1.0*$alpha/(Image::Magick->QuantumRange);
      print $coalesce->QueryColorname("rgba($red,$green,$blue,$alpha%)");
      my $depth=$coalesce->Get('depth');
      my $matte=$coalesce->Get('matte');
      if ($depth <= 8)
        {
          printf("  #%02X%02X%02X",int(255.0*$red/100.0),
            int(255.0*$green/100.0),int(255.0*$blue/100.0));
          printf("%02X",int(255.0-255.0*$alpha)) if $matte != 0;
        }
      else
        {
          if ($depth <= 16)
            {
              printf("  #%04X%04X%04X",int(65535.0*$red/100.0),
                int(65535.0*$green/100.0),int(65535.0*$blue/100.0));
              printf("%04X",65535.0-int(65535.0*$alpha)) if $matte != 0;
            }
          else
            {
              printf("  #%08X%08X%08X",int(4294967295.0*$red/100.0),
                int(4294967295.0*$green/100.0),int(4294967295.0*$blue/100.0));
              printf("%08X",4294967295.0-int(4294967295.0*$alpha)) if
                $matte != 0;
            }
        }
      print "</samp></pre></ul>\n";
    }
  if ($image->Get('error') != 0.0)
    {
      my $error=$image->Get('error');
      $error*=(Image::Magick->QuantumRange);
      print '<ul><pre class="highlight"><samp>';
      print 'Distortion: ' . $error . ' (' . $image->Get('error') . ')';
      print "</samp></pre></ul>\n";
    }
  print "<br />\n";
  print "<fieldset>\n";
  print "<legend>Paint Properties</legend>\n";
  print "<dl><dd>\n";
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\">Fuzz</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Paint.html\" target=\"help\">Method</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Paint.html\" target=\"help\">Paint Type</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,
    -value=>'0%'), "</td>\n";
  my @types=Image::Magick->QueryOption('method');
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Method',
    -values=>[@types]), "</td>\n";
  print '<td>', $q->popup_menu(-class=>'form-control',-name=>'Primitive',
    -values=>[@PrimitiveTypes]),"</td>\n";
  print "</tr>\n";
  print '</table><br />';
  print "<table class=\"table table-condensed table-striped\">\n";
  print "<tr>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Fill Color</a></th>\n";
  print "<th><a href=\"$DocumentDirectory/Color.html\" target=\"help\">Border Color</a></th>\n";
  print "</tr>\n";
  print "<tr>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'Color',
    -value=>'none',-size=>25), "</td>\n";
  print '<td>', $q->textfield(-class=>'form-control',-name=>'BorderColor',
    -value=>'none',-size=>25), "</td>\n";
  print "</tr>\n";
  print '</table>';
  print "</dd></dl>\n";
  print "</fieldset>\n";
  print $q->end_form, "\n";
  print <<XXX;
<br /> <br /> <br /> <br />
XXX
  ;
  Trailer(undef);
}

#
# Display a warning.
#
sub Warning
{
  my($message,$qualifier) = @_;

  Header($message);
  print <<XXX;
<br /> <br />
<dl>
<dt><font face="Arial,Helvetica" size=+3>$message:</font>
<br />
<dd><font face="Arial,Helvetica" size=+2>$qualifier</font>
</dl>
<br /> <br />
<br />
<br />
<br />
Press a tab above to continue.
XXX
  ;
  Trailer(1);
  die $message;
}

#
# Initialize the CGI context.
#
setpriority(0,0,getpriority(0,0)+4);  # be nice
$CGI::POST_MAX=1024*$MaxFilesize;
$timer=time;
$q=new CGI;
$q->autoEscape(undef);
if (GetAddress($q->virtual_host) == '198.72.81.86')
  {
    print $q->redirect('https://warrior.imagemagick.org/MagickStudio');
    exit;
  }
$q->delete('CacheID');
$q->param(-name=>'CacheID',-value=>rand($timer+$$));
#
# Choose function as determined by the query and environment.
#
$header=undef;
$action=$q->param('Action');
$q->delete('Action');
Upload() if defined($q->param('File'));
Upload() if defined($q->param('URL'));
UploadForm() unless defined($action);
my $session = $q->param('SessionID');
my $filename = Untaint($DocumentRoot . $DocumentDirectory .
  "/session_info/$session.Upload");
UploadForm() unless -e $filename;
Error('You must specify a filename or URL') unless $q->param('Path');
%Functions=
(
  'annotate'=>\&ChooseTool,
  'compare'=>\&ChooseTool,
  'composite'=>\&ChooseTool,
  'decorate'=>\&ChooseTool,
  'draw'=>\&ChooseTool,
  'effect'=>\&ChooseTool,
  'enhance'=>\&ChooseTool,
  'generate'=>\&ChooseTool,
  'identify'=>\&ChooseTool,
  'mogrify'=>\&Mogrify,
  'Mogrify'=>\&Mogrify,
  'output'=>\&ChooseTool,
  'quantize'=>\&ChooseTool,
  'resize'=>\&ChooseTool,
  'send'=>\&ChooseTool,
  'transform'=>\&ChooseTool,
  'upload'=>\&FileTransfer,
  'view'=>\&ChooseTool,
);
my $function = $Functions{$action};
&$function() if defined($function);
Error('Request failed due to malformed query');
