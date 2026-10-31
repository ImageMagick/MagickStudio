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
#  Copyright (C) 1999 ImageMagick Studio LLC, a non-profit organization       #
#  dedicated to making software imaging solutions freely available.           #
#                                                                             #
#  You may not use this file except in compliance with the License.  You may  #
#  obtain a copy of the License at                                            #
#                                                                             #
#    https://imagemagick.org/license/                                         #
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

use CGI::Fast;
use CGI::Carp qw/fatalsToBrowser/;
use Sys::Hostname;
use MagickStudio;
use strict;

#
# Global variable declarations.
#
my($action, %Functions, $header, $length, $prefix, $q, $request_count, %seen,
   $timer, $user_agent);

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
$ENV{LD_LIBRARY_PATH}='/usr/local/lib:/usr/lib64:/usr/lib';
$ENV{MAGICK_FONT_PATH}=$DocumentRoot . $DocumentDirectory . "/fonts";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
  getstore(Untaint(scalar $q->param('FontURL')),'MagickStudio.ttf')
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
      $status=$image->Polaroid(caption=>$text,font=>$font,fill=>$fill,
        stroke=>$stroke,strokewidth=>$strokewidth,pointsize=>$pointsize,
        angle=>$rotate,gravity=>$gravity,
        background=>$q->param('BackgroundColor'));
    }
  else
    {
      $status=$image->Annotate(text=>$text,geometry=>$geometry,font=>$font,
        fill=>$fill,stroke=>$stroke,strokewidth=>$strokewidth,
        undercolor=>$undercolor,pointsize=>$pointsize,density=>$density,
        gravity=>$gravity,kerning=>$kerning,
        'interline-spacing'=>$interline_spacing,
        'interword-spacing'=>$interword_spacing,translate=>$translate,
        scale=>$scale,rotate=>$rotate,skewX=>$skew_x,skewY=>$skew_y,
        antialias=>$antialias,direction=>$direction);
    }
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="card-title fw-bold mb-3">Annotate Image</h5>
    <p class="card-text text-secondary mb-0">To <a href="$DocumentDirectory/Annotate.html" target="help" class="text-decoration-none">annotate</a> your image with text, enter your text and location below and press <code>annotate</code>. Configure optional styling parameters as needed.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST', -class=>'needs-validation');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textarea(-class=>'form-control',-name=>'Text',-columns=>50,-rows=>3,-placeholder=>'Text',-style=>'height: 100px;'), "\n";
  print "<label for=\"Text\">Text to Annotate</label>\n";
  print "</div>\n";
  
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Geometry',-size=>25,-value=>'+0+0',-placeholder=>'Offset'), "\n";
  print "<label for=\"Geometry\">Offset</label>\n";
  print "</div>\n";
  print "</div>\n";
  
  my @types=Image::Magick->QueryOption('gravity');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Gravity',-values=>[@types],-default=>'SouthEast'), "\n";
  print "<label for=\"Gravity\">Gravity</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'annotate'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Annotate Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Fill',-value=>'white',-size=>25,-placeholder=>'Fill Color'), "\n";
  print "<label for=\"Fill\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Fill Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Stroke',-value=>'none',-size=>25,-placeholder=>'Stroke Color'), "\n";
  print "<label for=\"Stroke\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Stroke Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Undercolor',-value=>'none',-size=>25,-placeholder=>'Undercolor'), "\n";
  print "<label for=\"Undercolor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Undercolor</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Pointsize',-value=>'24',-size=>25,-placeholder=>'PointSize'), "\n";
  print "<label for=\"Pointsize\">PointSize</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Density',-value=>'90',-size=>25,-placeholder=>'Density'), "\n";
  print "<label for=\"Density\">Density</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'StrokeWidth',-value=>'0',-size=>25,-placeholder=>'Stroke Width'), "\n";
  print "<label for=\"StrokeWidth\">Stroke Width</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Kerning',-value=>'0',-size=>25,-placeholder=>'Kerning'), "\n";
  print "<label for=\"Kerning\">Kerning</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'InterlineSpacing',-value=>'0',-size=>25,-placeholder=>'Interline Spacing'), "\n";
  print "<label for=\"InterlineSpacing\">Interline Spacing</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'InterwordSpacing',-value=>'0',-size=>25,-placeholder=>'Interword Spacing'), "\n";
  print "<label for=\"InterwordSpacing\">Interword Spacing</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  $image=new Image::Magick;
  @fonts=$image->QueryFont();
  my @directions=Image::Magick->QueryOption('direction');
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->scrolling_list(-class=>'form-select',-name=>'Font',-values=>[@fonts],-size=>5, -style=>'height: 145px;'), "\n";
  print "<label for=\"Font\"><a href=\"$DocumentDirectory/fonts/\" class=\"text-decoration-none\">Font</a></label>\n";
  print "</div>\n";
  print "<div class=\"form-floating mt-2\">\n";
  print $q->textfield(-class=>'form-control',-name=>'FontURL',-value=>'http://',-size=>25,-placeholder=>'Font URL'), "\n";
  print "<label for=\"FontURL\">Custom Font URL</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Direction',-values=>[@directions]), "\n";
  print "<label for=\"Direction\">Direction</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Translate',-value=>'0.0, 0.0',-size=>25,-placeholder=>'Translate'), "\n";
  print "<label for=\"Translate\">Translate</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Scale',-value=>'1.0, 1.0',-size=>25,-placeholder=>'Scale'), "\n";
  print "<label for=\"Scale\">Scale</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Rotate',-value=>'0.0',-size=>25,-placeholder=>'Rotate'), "\n";
  print "<label for=\"Rotate\">Rotate</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SkewX',-value=>'0.0',-size=>25,-placeholder=>'Skew X'), "\n";
  print "<label for=\"SkewX\">Skew X</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SkewY',-value=>'0.0',-size=>25,-placeholder=>'Skew Y'), "\n";
  print "<label for=\"SkewY\">Skew Y</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BackgroundColor',-value=>'none',-size=>25,-placeholder=>'Background Color'), "\n";
  print "<label for=\"BackgroundColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Background Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mt-4\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Antialias',-label=>' Antialias text.',-checked=>'true'), "\n";
  print "</div>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Polaroid',-label=>' Simulate a Polaroid picture.'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
<div class="alert alert-warning shadow-sm border-0 p-4" role="alert">
  <h4 class="alert-heading fw-bold mb-2">Restricted Operating Hours</h4>
  <p class="mb-0"><code>ImageMagick Studio</code> has restricted access from 6PM until 11PM EST. We have temporarily <i>suspended</i> processing. Shortly after 11PM, processing <var>automagically</var> continues and your image will be returned.</p>
</div>
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
<div class="alert alert-danger shadow-sm border-0 p-4 mb-4" role="alert">
  <h4 class="alert-heading fw-bold mb-2">Server Busy</h4>
  <p class="mb-0"><code>ImageMagick Studio</code> is busy serving other requests. Processing has been temporarily suspended.</p>
</div>
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-0">
    <table class="table table-hover mb-0 text-center">
      <thead class="table-light">
        <tr>
          <th>Load Average</th>
          <th>Threshold</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="fw-semibold">$load_average</td>
          <td class="fw-semibold">$LoadAverageThreshold</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
<p class="text-secondary">When the load average drops below the threshold, processing will automatically continue. Retrying in $refresh_rate seconds.</p>
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
  SaveQueryState(scalar $q->param('SessionID'),$tooltype);
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
    %options, $parameter, $path, $status, $transparent_color);

  #
  # Read image.
  #
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Quantize image.
  #
  grep($options{$_}++,$q->param('Options'));
  $colors=$q->param('Parameter');
  $dither='no';
  $dither='Riemersma' if $options{'dither'};
  $global_colormap='false';
  $global_colormap='true' if $options{'global colormap'};
  $colorspace='sRGB';
  $colorspace='Gray' if $options{'gray'};
  $colorspace=$q->param('Colorspace') if $q->param('Colorspace');
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
  $status=$image->OrderedDither($parameter) if $options{'ordered dither'};
  $status=$image->Posterize(levels=>$levels,dither=>$dither) if
    $options{'posterize'};
  $status=$image->Segment(colorspace=>$colorspace) if $options{'segment'};
  $status=$image->Kmeans($parameter) if $options{'kmeans'};
  $status=$image->Quantize(colors=>$colors,dither=>$dither,
    colorspace=>$colorspace,'transparent-color'=>$transparent_color);
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="card-title fw-bold mb-3">Colormap Settings</h5>
    <p class="card-text text-secondary mb-0">Select options for creating or altering the image <a href="$DocumentDirectory/Colormap.html" target="help" class="text-decoration-none">colormap</a>. Options include color reduction, dithering, or grayscale conversion. Press <code>quantize</code> when ready.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'quantize'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Parameter',-size=>25,-value=>'256',-placeholder=>'Parameter'), "\n";
  print "<label for=\"Parameter\">Parameter</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Options</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->checkbox_group(-name=>'Options',-values=>@OptionTypes,-columns=>3,-default=>'dither',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'quantize'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Transform Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'TransparentColor',-value=>'none',-size=>25,-placeholder=>'Transparent Color'), "\n";
  print "<label for=\"TransparentColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Transparent Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  
  my @types=Image::Magick->QueryOption('colorspace');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Colorspace',-values=>[@types],-default=>'sRGB'), "\n";
  print "<label for=\"Colorspace\"><a href=\"$DocumentDirectory/Colorspace.html\" target=\"help\" class=\"text-decoration-none\">Colorspace</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
<div class="text-center my-4">
  <a href="$SponsorURL" target="sponsor">
    <img src="$DocumentDirectory/images/$SponsorIcon" alt="[sponsor]" class="float-end img-fluid ms-3" />
  </a>
  <img alt="ImageMagick Studio" src="$DocumentDirectory/images/magick.png" class="img-fluid" width="114" height="118" />
</div>
<hr class="my-4" />
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-3">Comment Received</h5>
    <div class="p-3 bg-body-tertiary rounded mb-3 border">
      <pre class="mb-0 overflow-auto" style="max-height: 50vh;"><code>@{[ $q->param('Comment') ]}</code></pre>
    </div>
    <div class="alert alert-info border-0 mb-0">An administrator will review your comment soon. Thank you!</div>
  </div>
</div>
XXX
  ;
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
<div class="text-center my-4">
  <a href="$SponsorURL" target="sponsor">
    <img src="$DocumentDirectory/images/$SponsorIcon" alt="[sponsor]" class="float-end img-fluid ms-3" />
  </a>
  <img alt="ImageMagick Studio" src="$DocumentDirectory/images/magick.png" class="img-fluid" width="114" height="118" />
</div>
<hr class="my-4" />
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Send Feedback</h5>
    <p class="text-secondary mb-0">If you have comments or problems with <code>ImageMagick Studio</code>, submit your details below. Include a valid email address if you require a response.</p>
  </div>
</div>
XXX
  ;
  $q->delete('Comment');
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textarea(-class=>'form-control',-name=>'Comment',-columns=>50,-rows=>10,-placeholder=>'Comment',-style=>'height: 180px;'), "\n";
  print "<label for=\"Comment\">Your Comment</label>\n";
  print "</div>\n";
  
  print "<div class=\"d-flex gap-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'send'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
  print $q->end_html;
  die "FCGI_DONE\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Read compare image.
  #
  if ($q->param('CompareURL')) {
    $filename=Untaint(scalar $q->param('CompareURL'));
    getstore($filename,'MagickStudio.dat');
  } else {
    $filename=Untaint(scalar $q->param('CompareFile')) if $q->param('CompareFile');
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Compare Images</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Compare.html" target="help" class="text-decoration-none">compare</a> images, select a local file or enter a remote URL. Choose parameters and click <code>compare</code>.</p>
  </div>
</div>
XXX
  ;
  $action=$q->script_name() . "?CacheID=" . $q->param('CacheID') .
    ";Action=compare";
  print $q->start_multipart_form(-action=>$action,-method=>'POST');
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"mb-3\">\n";
  print "<label class=\"form-label fw-bold\"><a href=\"$DocumentDirectory/Filename.html\" target=\"help\" class=\"text-decoration-none\">Filename</a></label>\n";
  print $q->filefield(-class=>'form-control',-name=>'CompareFile',-size=>50,-maxlength=>1024), "\n";
  print "</div>\n";

  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'CompareURL',-size=>50,-placeholder=>'URL'), "\n";
  print "<label for=\"CompareURL\"><a href=\"$DocumentDirectory/URL.html\" target=\"help\" class=\"text-decoration-none\">URL</a></label>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'compare'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Compare Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,-value=>'0%',-placeholder=>'Fuzz'), "\n";
  print "<label for=\"Fuzz\"><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\" class=\"text-decoration-none\">Fuzz</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  my @types=Image::Magick->QueryOption('metric');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'MetricType',-values=>[@types],-default=>'NCC'), "\n";
  print "<label for=\"MetricType\"><a href=\"$DocumentDirectory/Metric.html\" target=\"help\" class=\"text-decoration-none\">Metric</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  my @channels=Image::Magick->QueryOption('channel');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'ChannelType',-values=>[@channels],-default=>'Default'), "\n";
  print "<label for=\"ChannelType\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel Type</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"form-check mt-3\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Clipboard',-label=>' Use clipboard image as source for compare.'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Read composite image.
  #
  if ($q->param('CompositeURL')) {
    $filename=Untaint(scalar $q->param('CompositeURL'));
    getstore($filename,'MagickStudio.dat');
  } else {
    $filename=Untaint(scalar $q->param('CompositeFile')) if $q->param('CompositeFile');
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
    $status=$slice->Resize(width=>$image->[$i]->Get('width'),
      height=>$image->[$i]->Get('height')) if $q->param('Resize') eq 'on';
    $status=$image->[$i]->Composite(compose=>$compose,image=>$slice,
      gravity=>$gravity,geometry=>$geometry,rotate=>$rotate,color=>$color,
      tile=>$tile);
    Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Composite Image</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Composite.html" target="help" class="text-decoration-none">composite</a> images, upload a file or specify a remote URL. Select placement and composition parameters, then press <code>composite</code>.</p>
  </div>
</div>
XXX
  ;
  $action=$q->script_name() . "?CacheID=" . $q->param('CacheID') .
    ";Action=composite";
  print $q->start_multipart_form(-action=>$action,-method=>'POST');
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"mb-3\">\n";
  print "<label class=\"form-label fw-bold\"><a href=\"$DocumentDirectory/Filename.html\" target=\"help\" class=\"text-decoration-none\">Filename</a></label>\n";
  print $q->filefield(-class=>'form-control',-name=>'CompositeFile',-size=>50,-maxlength=>1024), "\n";
  print "</div>\n";

  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'CompositeURL',-size=>50,-placeholder=>'URL'), "\n";
  print "<label for=\"CompositeURL\"><a href=\"$DocumentDirectory/URL.html\" target=\"help\" class=\"text-decoration-none\">URL</a></label>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Geometry',-size=>25,-value=>'+0+0',-placeholder=>'Offset'), "\n";
  print "<label for=\"Geometry\">Offset</label>\n";
  print "</div>\n";
  print "</div>\n";

  my @types=Image::Magick->QueryOption('gravity');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Gravity',-values=>[@types],-default=>'Center'), "\n";
  print "<label for=\"Gravity\">Gravity</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'composite'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Composite Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Blend',-size=>25,-value=>'0%',-placeholder=>'Blend'), "\n";
  print "<label for=\"Blend\">Blend</label>\n";
  print "</div>\n";
  print "</div>\n";

  my @compose_types=Image::Magick->QueryOption('compose');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'ComposeType',-values=>[@compose_types],-default=>'SrcOver'), "\n";
  print "<label for=\"ComposeType\">Compose</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Rotate',-size=>25,-value=>'0.0',-placeholder=>'Rotate'), "\n";
  print "<label for=\"Rotate\">Rotate</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BackgroundColor',-value=>'none',-size=>25,-placeholder=>'Background Color'), "\n";
  print "<label for=\"BackgroundColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Background Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mt-3\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Tile',-label=>' Tile across and down the image canvas.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Resize',-label=>' Resize to fit.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Clipboard',-label=>' Use clipboard image as source for composite.'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  umask(002);
  $digest=Digest::SHA3->new(512);
  $digest->add($HashDigestSalt,$q->remote_addr(),time(),{},rand(),$$);
  $path.='/' . $digest->hexdigest;
  $ENV{TMPDIR}=$path;
  mkdir($path,0775);
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
  $status=$image->Border(geometry=>$geometry,bordercolor=>$color,
    compose=>$compose) if $q->param('Option') eq 'border *';
  $status=$image->Frame(geometry=>$geometry,fill=>$color,compose=>$compose)
    if $q->param('Option') eq 'frame *';
  $status=$image->Raise(geometry=>$geometry,raise=>'true')
    if $q->param('Option') eq 'raise *';
  $status=$image->Raise(geometry=>$geometry,raise=>'False')
    if $q->param('Option') eq 'sunken *';
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Decorate Image</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Decorate.html" target="help" class="text-decoration-none">decorate</a> your image with a border or frame, configure parameters below and press <code>decorate</code>.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Geometry',-size=>25,-value=>'15x15+3+3',-placeholder=>'Decoration Geometry'), "\n";
  print "<label for=\"Geometry\">Decoration Geometry</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Color',-size=>25,-value=>'gray',-placeholder=>'Color'), "\n";
  print "<label for=\"Color\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Choose Decoration</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>4,-default=>'frame *',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'decorate'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Decorate Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  my @types=Image::Magick->QueryOption('compose');
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'ComposeType',-values=>[@types],-default=>'SrcOver'), "\n";
  print "<label for=\"ComposeType\">Compose</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
      $append_image=$image->Append(stack=>$value);
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
  for ($i=0; $i < scalar(@$image); $i++)
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
  for ($i=0; $i < scalar(@$image); $i++)
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4 text-center">
    <h5 class="fw-bold mb-3">Converted Image</h5>
    <p class="text-secondary mb-3">Click on any image to view or Shift-click to download to your local drive. Click <code>upload</code> to transfer to a remote server.</p>
XXX
  ;
  if ($#$image > 0)
    {
      #
      # Display animated image.
      #
      ($width,$height)=$image->Get('width','height');
      print <<XXX;
    <div class="mb-3">
      <a href="$url/$basename.$format"> <img alt="$basename.$format" src="$url/Animate.gif" width=$width height=$height class="img-fluid rounded border shadow-sm" /></a>
    </div>
XXX
  ;
    }
  ($width,$height)=$montage->Get('width','height');
  print <<XXX;
    <div class="mb-3">
      <img ismap usemap="#Montage" src="$url/MagickStudio.gif" width=$width height=$height class="img-fluid rounded border shadow-sm" />
    </div>
    <map name="Montage">
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
XXX
  ;
  if ($q->param('Option') eq 'clipboard') {
    print '<p class="text-muted small fst-italic mt-2 mb-0">* This image was saved to the ImageMagick Studio clipboard.</p>';
  }
  print "</div></div>\n";
  #
  # Image upload form.
  #
  RestoreQueryState($q->param('SessionID'),$q->param('Path'),'FileTransfer');
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'upload'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Upload Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  $hostname=GetHostname($q->remote_host());
  $username='anonymous';
  $username=$q->remote_user() if $q->remote_user();

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Hostname',-size=>50,-value=>$hostname,-placeholder=>'FTP Hostname'), "\n";
  print "<label for=\"Hostname\"><a href=\"$DocumentDirectory/Upload.html\" target=\"help\" class=\"text-decoration-none\">FTP Server Name</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Username',-size=>25,-value=>$username,-placeholder=>'Account Name'), "\n";
  print "<label for=\"Username\"><a href=\"$DocumentDirectory/Upload.html\" target=\"help\" class=\"text-decoration-none\">Account Name</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->password_field(-class=>'form-control',-name=>'Password',-size=>25,-placeholder=>'Password'), "\n";
  print "<label for=\"Password\"><a href=\"$DocumentDirectory/Upload.html\" target=\"help\" class=\"text-decoration-none\">Password</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Directory',-size=>50,-placeholder=>'Directory'), "\n";
  print "<label for=\"Directory\"><a href=\"$DocumentDirectory/Upload.html\" target=\"help\" class=\"text-decoration-none\">Upload Directory</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Filename',-size=>50,-value=>"$basename.$format",-placeholder=>'Filename'), "\n";
  print "<label for=\"Filename\"><a href=\"$DocumentDirectory/Upload.html\" target=\"help\" class=\"text-decoration-none\">Filename</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'upload'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Display Download form.
  #
  Header(GetTitle($image));
  print <<XXX;
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Download Image</h5>
    <p class="text-secondary mb-0">Select an <a href="$DocumentDirectory/Download.html" target="help" class="text-decoration-none">output</a> format and configure attributes. Press <code>output</code> to convert and download the file.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'output'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  $format=$q->param('Magick');
  @formats=$image->QueryFormat();
  print "<div class=\"form-floating mb-3\">\n";
  print $q->scrolling_list(-class=>'form-select',-name=>'Format',-values=>[@formats],-size=>5,-default=>$format), "\n";
  print "<label for=\"Format\"><a href=\"$DocumentDirectory/Format.html\" target=\"help\" class=\"text-decoration-none\">Format</a></label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\"><a href=\"$DocumentDirectory/Storage.html\" target=\"help\" class=\"text-decoration-none\">Storage Type</a></label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>3,-default=>'multi-frame file',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'output'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Download Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  
  my @type_opts=Image::Magick->QueryOption('type');
  my @compress_opts=Image::Magick->QueryOption('compress');
  my @channels=Image::Magick->QueryOption('channel');
  my @alpha_opts=Image::Magick->QueryOption('Alpha');

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Type',-values=>[@type_opts]), "\n";
  print "<label for=\"Type\">Image Type</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Compress',-values=>[@compress_opts]), "\n";
  print "<label for=\"Compress\">Compress</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Channel',-values=>[@channels],-default=>'All'), "\n";
  print "<label for=\"Channel\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Alpha',-values=>[@alpha_opts],-default=>'Undefined'), "\n";
  print "<label for=\"Alpha\">Alpha</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  my @dispose_opts=Image::Magick->QueryOption('dispose');
  my @interlace_opts=Image::Magick->QueryOption('interlace');
  my @preview_opts=Image::Magick->QueryOption('preview');

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Dispose',-values=>[@dispose_opts],-default=>'Undefined'), "\n";
  print "<label for=\"Dispose\">Dispose</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Interlace',-values=>[@interlace_opts],-default=>'None'), "\n";
  print "<label for=\"Interlace\"><a href=\"$DocumentDirectory/Interlace.html\" target=\"help\" class=\"text-decoration-none\">Interlace</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Preview',-values=>[@preview_opts]), "\n";
  print "<label for=\"Preview\">Preview</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Delay',-size=>15,-value=>$image->Get('delay'),-placeholder=>'Delay'), "\n";
  print "<label for=\"Delay\"><a href=\"$DocumentDirectory/Delay.html\" target=\"help\" class=\"text-decoration-none\">Delay</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Loop',-size=>15,-value=>$image->Get('loop'),-placeholder=>'Loop'), "\n";
  print "<label for=\"Loop\"><a href=\"$DocumentDirectory/Loop.html\" target=\"help\" class=\"text-decoration-none\">Loop</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Quality',-size=>15,-value=>$image->Get('quality'),-placeholder=>'Quality'), "\n";
  print "<label for=\"Quality\"><a href=\"$DocumentDirectory/Quality.html\" target=\"help\" class=\"text-decoration-none\">Quality</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Depth',-size=>25,-value=>$image->Get('depth'),-placeholder=>'Image Depth'), "\n";
  print "<label for=\"Depth\">Image Depth</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Offset',-size=>25,-value=>2,-placeholder=>'Smush Offset'), "\n";
  print "<label for=\"Offset\">Smush Offset</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Page',-size=>25,-placeholder=>'Page Geometry'), "\n";
  print "<label for=\"Page\"><a href=\"$DocumentDirectory/Page.html\" target=\"help\" class=\"text-decoration-none\">Page Geometry</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-3\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Passphrase',-size=>25,-placeholder=>'Passphrase'), "\n";
  print "<label for=\"Passphrase\"><a href=\"$DocumentDirectory/Passphrase.html\" target=\"help\" class=\"text-decoration-none\">Passphrase</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"form-floating mb-3\">\n";
  print $q->textarea(-class=>'form-control',-name=>'Comment',-columns=>50,-rows=>3,-value=>$image->Get('comment'),-placeholder=>'Comment',-style=>'height: 80px;'), "\n";
  print "<label for=\"Comment\">Comment</label>\n";
  print "</div>\n";

  print "<div class=\"mt-3\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Repage',-label=>' Reset page geometry.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Coalesce',-checked=>'true',-label=>' Coalesce multi-frame images.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Strip',-label=>' Strip image of comments or profiles.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'CMYK',-label=>' Save image as CMYK pixels (JPEG, TIFF, PS, PDF, PSD).'), "\n";
  print "</div>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Stack',-label=>' Stack images left-to-right (when storage type is append).'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
      $status=$image->Draw(primitive=>$primitive,fill=>$fill,stroke=>$stroke,
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
      $status=$image->Draw(primitive=>$primitive,fill=>$fill,stroke=>$stroke,
        strokewidth=>$strokewidth,tile=>$tile,points=>$points,x=>$x,y=>$y,
        translate=>$translate,scale=>$scale,rotate=>$rotate,skewX=>$skew_x,
        skewY=>$skew_y,antialias=>$antialias);
    }
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Draw Vector Graphics</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Draw.html" target="help" class="text-decoration-none">draw</a> on your image, select a primitive, specify coordinates, and press <code>draw</code>.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  my @types=Image::Magick->QueryOption('primitive');
  print "<div class=\"form-floating mb-3\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Primitive',-values=>[@types],-default=>'Line'), "\n";
  print "<label for=\"Primitive\">Primitive</label>\n";
  print "</div>\n";

  print "<div class=\"form-floating mb-3\">\n";
  print $q->textarea(-class=>'form-control',-name=>'Coordinates',-columns=>50,-rows=>2,-value=>'+10+10  +60+60',-placeholder=>'Coordinates',-style=>'height: 80px;'), "\n";
  print "<label for=\"Coordinates\">Coordinates</label>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'draw'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Draw Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Fill',-value=>'white',-size=>25,-placeholder=>'Fill Color'), "\n";
  print "<label for=\"Fill\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Fill Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Stroke',-value=>'none',-size=>25,-placeholder=>'Stroke Color'), "\n";
  print "<label for=\"Stroke\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Stroke Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'StrokeWidth',-value=>'1',-size=>25,-placeholder=>'Stroke Width'), "\n";
  print "<label for=\"StrokeWidth\">Stroke Width</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Translate',-value=>'0.0, 0.0',-size=>25,-placeholder=>'Translate'), "\n";
  print "<label for=\"Translate\">Translate</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Scale',-value=>'1.0, 1.0',-size=>25,-placeholder=>'Scale'), "\n";
  print "<label for=\"Scale\">Scale</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Rotate',-value=>'0.0',-size=>25,-placeholder=>'Rotate'), "\n";
  print "<label for=\"Rotate\">Rotate</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SkewX',-value=>'0.0',-size=>25,-placeholder=>'Skew X'), "\n";
  print "<label for=\"SkewX\">Skew X</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SkewY',-value=>'0.0',-size=>25,-placeholder=>'Skew Y'), "\n";
  print "<label for=\"SkewY\">Skew Y</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mt-3\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Tile',-label=>' Paint the drawing primitive with the clipboard image.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Antialias',-label=>' Antialias text.',-checked=>'true'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Effects image.
  #
  $parameter=$q->param('Parameter');
  $channel=$q->param('Channel');
  $image->Set('virtual-pixel'=>scalar $q->param('VirtualPixelMethod')) if
    $q->param('VirtualPixelMethod');
  $image->Set(label=>$q->param('Label')) if $q->param('Label');
  $status=$image->AdaptiveBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'adaptive blur *';
  $status=$image->AdaptiveSharpen(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'adaptive sharpen *';
  $status=$image->BilateralBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'bilateral blur *';
  $status=$image->BlackThreshold(geomery=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'black threshold *';
  $status=$image->Blur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'blur *';
  $status=$image->Charcoal("$parameter") if $q->param('Option') eq
     'charcoal drawing *';
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
  $status=$image->ConnectedComponents("$parameter") if $q->param('Option') eq
    'connected components *';
  if ($q->param('Option') eq 'convolve *')
    {
      my(@coefficients);

      @coefficients=split(/[ ,]+/,$parameter);
      $status=$image->Convolve(\@coefficients);
    }
  $status=$image->Despeckle() if $q->param('Option') eq 'despeckle';
  if ($q->param('Option') eq 'distort *')
    {
      my(@points, $method);

      @points=split(/[ ,]+/,$parameter);
      $method=$q->param('DistortType');
      $status=$image->Distort(method=>$method,points=>\@points);
    }
  if ($q->param('Option') eq 'evaluate *')
    {
      my(@values, $operator);

      @values=split(/[ ,]+/,$parameter);
      $operator=$q->param('EvaluateType');
      $status=$image->Evaluate(operator=>$operator,value=>\@values);
    }
  if ($q->param('Option') eq 'function *')
    {
      my(@parameters, $function);

      @parameters=split(/[ ,]+/,$parameter);
      $function=$q->param('FunctionType');
      $status=$image->Function(function=>$function,parameters=>\@parameters);
    }
  $status=$image->CannyEdge("$parameter") if $q->param('Option') eq
    'canny edge *';
  $status=$image->Edge("$parameter") if $q->param('Option') eq 'edge detect *';
  $status=$image->Emboss(geometry=>$parameter) if $q->param('Option') eq
    'emboss *';
  $status=$image->ForwardFourierTransform("$parameter") if
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
            {
              $status=$image->ChannelFx(image=>$source,expression=>$parameter);
            }
          else
            {
              $status=$image->ChannelFx(image=>$source,channel=>$channel,
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
            { $status=$image->Fx(image=>$source,expression=>$parameter); }
          else
            {
              $status=$image->Fx(image=>$source,channel=>$channel,
                expression=>$parameter);
            }
          Error($image) if !ref($image);
        }
    }
  $status=$image->GaussianBlur(geometry=>"$parameter",channel=>$channel) if
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
        { $status=$image->HaldClut(image=>$source); }
      else
        { $status=$image->HaldClut(image=>$source,channel=>$channel); }
      Error($image) if !ref($image);
    }
  $status=$image->HoughLine("$parameter") if $q->param('Option') eq
    'hough line *';
  $status=$image->Implode("$parameter") if $q->param('Option') eq 'implode *';
  $status=$image->Integral() if $q->param('Option') eq 'integral';
  $status=$image->InverseFourierTransform("$parameter") if
    $q->param('Option') eq 'inverse Fourier transform';
  $status=$image->Kuwahara(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'kuwahara *';
  $status=$image->MeanShift("$parameter") if $q->param('Option') eq
    'mean shift *';
  $status=$image->Mode("$parameter") if $q->param('Option') eq 'mode *';
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
      $status=$image->Morphology(kernel=>$parameter,method=>$method,
        channel=>$channel);
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
  $status=$image->MotionBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'motion blur *';
  $status=$image->MedianFilter("$parameter") if
    $q->param('Option') eq 'median filter *';
  $status=$image->OilPaint("$parameter") if $q->param('Option') eq
    'oil paint *';
  if ($q->param('Option') eq 'color-matrix *')
    {
      my(@coefficients);

      @coefficients=split(/[ ,]+/,$parameter);
      $status=$image->ColorMatrix(\@coefficients);
    }
  $status=$image->RangeThreshold(geomery=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'range threshold *';
  $status=$image->ReduceNoise("$parameter") if $q->param('Option') eq
    'reduce noise *';
  $status=$image->RotationalBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'rotational blur *';
  $status=$image->SelectiveBlur(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq '-class=>"checkbox",selective blur *';
  $status=$image->SepiaTone("$parameter") if $q->param('Option') eq
    'sepia tone *';
  $status=$image->Shade(geometry=>$parameter,gray=>'false')
    if $q->param('Option') eq 'shade *';
  $status=$image->Shade(geometry=>$parameter,gray=>'true')
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
  $status=$image->Sharpen(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'sharpen *';
  $status=$image->Sketch("$parameter") if $q->param('Option') eq 'sketch *';
  $status=$image->Solarize("$parameter") if $q->param('Option') eq 'solarize *';
  $status=$image->Spread("$parameter") if $q->param('Option') eq 'spread *';
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
      $status=$image->Stegano(image=>$clipboard);
    }
  if ($q->param('Option') eq 'stereo')
    {
      my($stereo);

      $stereo=$image->Clone();
      $stereo->Roll('+4+4');
      $status=$image->Stereo(image=>$stereo);
    }
  $status=$image->Swirl("$parameter") if $q->param('Option') eq 'swirl *';
  $status=$image->AdaptiveThreshold("$parameter") if
    $q->param('Option') eq 'adaptive threshold *';
  $status=$image->AutoThreshold() if $q->param('Option') eq 'auto-threshold';
  $status=$image->Threshold(threshold=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'threshold *';
  $status=$image->Tint(fill=>$q->param('FillColor'),opacity=>$parameter) if
    $q->param('Option') eq 'tint';
  $status=$image->UnsharpMask(geometry=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'unsharp mask *';
  $status=$image->Vignette(geometry=>"$parameter",background=>
    $q->param('BackgroundColor')) if $q->param('Option') eq 'vignette *';
  $status=$image->Wave("$parameter") if $q->param('Option') eq 'wave *';
  $status=$image->WaveletDenoise("$parameter") if
    $q->param('Option') eq 'wavelet denoise *';
  $status=$image->WhiteThreshold(threshold=>"$parameter",channel=>$channel) if
    $q->param('Option') eq 'white threshold *';
  $status=$image->Set(page=>'0x0+0+0') if $q->param('Repage') eq 'on';
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Apply Effects</h5>
    <p class="text-secondary mb-0">To apply an <a href="$DocumentDirectory/Effects.html" target="help" class="text-decoration-none">effect</a> to your image, select the method and set the parameter value if required (*). Press <code>effect</code> to process.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'effect'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Parameter',-size=>25,-value=>'0.0x1.0',-placeholder=>'Parameter'), "\n";
  print "<label for=\"Parameter\">Parameter</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Choose Effect</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>3,-default=>'sharpen',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'effect'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Effects Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3\">\n";
  
  my @methods=Image::Magick->QueryOption('virtual-pixel');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'VirtualPixelMethod',-values=>[@methods]), "\n";
  print "<label for=\"VirtualPixelMethod\">Virtual Pixel Method</label>\n";
  print "</div>\n";
  print "</div>\n";

  my @channels=Image::Magick->QueryOption('channel');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Channel',-values=>[@channels],-default=>'Default'), "\n";
  print "<label for=\"Channel\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
  $status=$image->Set('virtual-pixel'=>$q->param('VirtualPixelMethod')) if
    $q->param('VirtualPixelMethod');
  $status=$image->AutoGamma() if $q->param('Option') eq 'auto-gamma';
  $status=$image->AutoLevel() if $q->param('Option') eq 'auto-level';
  $status=$image->BrightnessContrast(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'brightness-contrast *';
  $status=$image->CLAHE("$parameter") if $q->param('Option') eq 'calhe *';
  $status=$image->Contrast(sharpen=>'true') if $q->param('Option') eq 'spiff';
  $status=$image->Contrast(sharpen=>'false') if $q->param('Option') eq 'dull';
  $status=$image->ContrastStretch(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'contrast-stretch *';
  $status=$image->Equalize(channel=>$channel) if $q->param('Option') eq
    'equalize';
  $status=$image->Gamma(gamma=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'gamma *';
  $status=$image->Level(levels=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'level *';
  $status=$image->LinearStretch($parameter) if $q->param('Option') eq
    'linear-stretch *';
  $status=$image->Modulate(hue=>$parameter) if $q->param('Option') eq 'hue *';
  $status=$image->Modulate(saturation=>$parameter)
    if $q->param('Option') eq 'saturation *';
  $status=$image->Modulate(brightness=>$parameter)
    if $q->param('Option') eq 'brightness *';
  $status=$image->Normalize(channel=>$channel) if $q->param('Option') eq
    'normalize';
  $status=$image->Negate(channel=>$channel) if $q->param('Option') eq 'negate';
  $status=$image->SigmoidalContrast(geometry=>$parameter,channel=>$channel) if
    $q->param('Option') eq 'sigmoidal-contrast *';
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Enhance Image</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Enhance.html" target="help" class="text-decoration-none">enhance</a> your image, select the method and supply a parameter if required (*). Press <code>enhance</code> to continue.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'enhance'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Parameter',-size=>25,-value=>'1.6',-placeholder=>'Parameter'), "\n";
  print "<label for=\"Parameter\">Parameter</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Choose Enhancement</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>3,-default=>'gamma *',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'enhance'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Enhance Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3\">\n";
  
  my @methods=Image::Magick->QueryOption('virtual-pixel');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'VirtualPixelMethod',-values=>[@methods]), "\n";
  print "<label for=\"VirtualPixelMethod\">Virtual Pixel Method</label>\n";
  print "</div>\n";
  print "</div>\n";

  my @channels=Image::Magick->QueryOption('channel');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Channel',-values=>[@channels],-default=>'Default'), "\n";
  print "<label for=\"Channel\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
<div class="card border-danger shadow-sm mb-4">
  <div class="card-body p-4 text-center">
    <div class="text-danger mb-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-exclamation-octagon-fill" viewBox="0 0 16 16">
        <path d="M11.46 1e-3M11.46.1L15.9 4.54c.09.09.14.21.14.34v6.24c0 .13-.05.25-.14.34L11.46 15.9c-.09.09-.21.14-.34.14H4.88c-.13 0-.25-.05-.34-.14L.1 11.46a.5.5 0 0 1-.14-.34V4.88c0-.13.05-.25.14-.34L4.54.1c.09-.09.21-.14.34-.14h6.24c.13 0 .25.05.34.14zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
      </svg>
    </div>
    <h4 class="card-title text-danger fw-bold mb-2">$message</h4>
    <p class="card-text text-secondary mb-1">$qualifier</p>
    <p class="card-text text-muted small mb-3"><code>$!</code></p>
    <p class="text-secondary mb-0">Press <code>Back</code> to correct the error or choose a navigation item above.</p>
  </div>
</div>
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

  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Special Effects (F/X)</h5>
    <p class="text-secondary mb-0">To apply special <a href="$DocumentDirectory/FX.html" target="help" class="text-decoration-none">effects</a>, choose an option and supply parameter values if required (*). Press <code>effect</code> to execute.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'effect'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Parameter',-size=>25,-value=>'60',-placeholder=>'Parameter'), "\n";
  print "<label for=\"Parameter\">Parameter</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Choose Special Effect</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>3,-default=>'swirl *',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'effect'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">F/X Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  
  my @distorts=Image::Magick->QueryOption('distort');
  my @operators=Image::Magick->QueryOption('evaluate');
  my @functions=Image::Magick->QueryOption('function');

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'DistortType',-values=>[@distorts],-default=>'Arc'), "\n";
  print "<label for=\"DistortType\">Distort Type</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'EvaluateType',-values=>[@operators],-default=>'Sin'), "\n";
  print "<label for=\"EvaluateType\">Evaluate Type</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'FunctionType',-values=>[@functions],-default=>'Sin'), "\n";
  print "<label for=\"FunctionType\">Function Type</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  my @morph_methods=Image::Magick->QueryOption('morphology');
  my @virt_methods=Image::Magick->QueryOption('virtual-pixel');
  my @channels=Image::Magick->QueryOption('channel');

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'MorphologyMethod',-values=>[@morph_methods]), "\n";
  print "<label for=\"MorphologyMethod\">Morphology Method</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'VirtualPixelMethod',-values=>[@virt_methods]), "\n";
  print "<label for=\"VirtualPixelMethod\">Virtual Pixel Method</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Channel',-values=>[@channels],-default=>'Default'), "\n";
  print "<label for=\"Channel\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BackgroundColor',-value=>'black',-size=>25,-placeholder=>'Background Color'), "\n";
  print "<label for=\"BackgroundColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Background Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'FillColor',-value=>'white',-size=>25,-placeholder=>'Fill Color'), "\n";
  print "<label for=\"FillColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Fill Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mt-3\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check mb-2\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Repage',-checked=>'true',-label=>' Reset page geometry.'), "\n";
  print "</div>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Clipboard',-label=>' Use clipboard image as source for F(x).'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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

      $path=Untaint(scalar $q->param('Path'));
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
  print $q->header(-charset=>'UTF-8',expires=>$ExpireCache,@attributes), "\n";
  print $q->start_html(
    -meta=>{
      'charset'=>'utf-8', 
      'viewport'=>'width=device-width, initial-scale=1, viewport-fit=cover'
    },
    -title=>$title,-author=>$ContactInfo,-encoding=>'UTF-8',
    -style=>{
      -src=>"$DocumentDirectory/assets/magick-css.php"
    },
    -head=>[
      "<link rel=\"icon\" href=\"$DocumentDirectory/images/wand.png\"/>",
      "<link rel=\"shortcut icon\" href=\"$DocumentDirectory/images/wand.ico\" type=\"image/x-icon\"/>",
      "<link rel=\"preload\" href=\"https://cdn.jsdelivr.net/npm/bootstrap\@5.3.8/dist/css/bootstrap.min.css\" as=\"style\" crossorigin=\"anonymous\">",
      "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap\@5.3.8/dist/css/bootstrap.min.css\" crossorigin=\"anonymous\">",
      "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3129977114552745\" crossorigin=\"anonymous\"></script>"
    ],
  ), "\n";
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
  <script>
    function setTheme(theme) {
      localStorage.setItem('theme', theme);
      updateThemeIcon(theme);
      document.documentElement.setAttribute('data-bs-theme', theme === 'auto' ? getSystemTheme() : theme);
    }
    function getSystemTheme() {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    function updateThemeIcon(theme) {
      const iconMap = {
        light: '☀️',
        dark: '🌙',
        auto: '🌓'
      };
      document.getElementById('currentThemeIcon').textContent = iconMap[theme] || '🌓';
    }
    document.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('theme') || 'auto';
      setTheme(savedTheme);
    });
  </script>
  <nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4 fixed-top shadow-sm">
  <div class="container-xl">
    <a class="navbar-brand fw-bold d-flex align-items-center gap-2" href="$DocumentDirectory/">
      <img id="icon" alt="ImageMagick Online Studio" width="32" height="32" src="$DocumentDirectory/images/wand.png"/>
      <span>Magick Studio</span>
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#magick-navbars" aria-controls="magick-navbars" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="magick-navbars">
      <ul class="navbar-nav me-auto mb-2 mb-md-0">
        <li class="nav-item ms-md-2 dropdown">
          <a class="nav-link dropdown-toggle $tools{'View'} $tools{'Identify'}" href="#" id="view" data-bs-toggle="dropdown" aria-expanded="false">View</a>
          <ul class="dropdown-menu shadow border-0" aria-labelledby="view">
            <li><a class="dropdown-item" href="$url;ToolType=View">View</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Identify">Identify</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Transform'} $tools{'Resize'}" href="#" id="transform" data-bs-toggle="dropdown" aria-expanded="false">Transform</a>
          <ul class="dropdown-menu shadow border-0" aria-labelledby="transform">
            <li><a class="dropdown-item" href="$url;ToolType=Transform">Transform</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Resize">Resize</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Effects'} $tools{'F/X'} $tools{'Enhance'} $tools{'Colormap'}" href="#" id="effects" data-bs-toggle="dropdown" aria-expanded="false">Effects</a>
          <ul class="dropdown-menu shadow border-0" aria-labelledby="effects">
            <li><a class="dropdown-item" href="$url;ToolType=Effects">Effects</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=FX">F/X</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Enhance">Enhance</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Colormap">Colormap</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Decorate'} $tools{'Annotate'} $tools{'Draw'}" href="#" id="decorate" data-bs-toggle="dropdown" aria-expanded="false">Decorate</a>
          <ul class="dropdown-menu shadow border-0" aria-labelledby="decorate">
            <li><a class="dropdown-item" href="$url;ToolType=Decorate">Decorate</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Annotate">Annotate</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Draw">Draw</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle $tools{'Composite'} $tools{'Compare'}" href="#" id="composite" data-bs-toggle="dropdown" aria-expanded="false">Composite</a>
          <ul class="dropdown-menu shadow border-0" aria-labelledby="composite">
            <li><a class="dropdown-item" href="$url;ToolType=Composite">Composite</a></li>
            <li><a class="dropdown-item" href="$url;ToolType=Compare">Compare</a></li>
          </ul>
        </li>
      </ul>
      <div class="d-flex align-items-center gap-2">
        <form class="d-flex m-0" action="$script">
          <input type="hidden" name="CacheID" value="$cacheID" />
          <input type="hidden" name="SessionID" value="$sessionID" />
          <input type="hidden" name="Path" value="$path" />
          <input type="hidden" name="Name" value="$name" />
          <input type="hidden" name="Magick" value="$magick" />
          <input type="hidden" name="ToolType" value="Upload" />
          <button class="btn btn-outline-light btn-sm fw-semibold px-3" type="submit">Upload</button>
        </form>
        <form class="d-flex m-0" action="$script">
          <input type="hidden" name="Action" value="mogrify" />
          <input type="hidden" name="CacheID" value="$cacheID" />
          <input type="hidden" name="SessionID" value="$sessionID" />
          <input type="hidden" name="Path" value="$path" />
          <input type="hidden" name="Name" value="$name" />
          <input type="hidden" name="Magick" value="$magick" />
          <input type="hidden" name="ToolType" value="Download" />
          <button class="btn btn-success btn-sm fw-semibold px-3" type="submit">Download</button>
        </form>
        <div class="dropdown">
          <a class="nav-link dropdown-toggle px-2" href="#" id="themeDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            <span id="currentThemeIcon">🌓</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end shadow border-0" aria-labelledby="themeDropdown">
            <li><a class="dropdown-item" href="#" onclick="setTheme('light')">☀️ Light</a></li>
            <li><a class="dropdown-item" href="#" onclick="setTheme('dark')">🌙 Dark</a></li>
            <li><a class="dropdown-item" href="#" onclick="setTheme('auto')">🌓 Auto</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  </nav>

<div class="container-xl px-4 pt-5 mt-4">
  <div class="row">
    <!-- Main Content Column (~80% width on large screens) -->
    <main role="main" class="col-lg-10 col-xl-10 px-3">
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-3">Image Information: <code>$filename</code></h5>
    <div class="bg-body-tertiary rounded border p-3">
      <pre class="mb-0 overflow-auto text-body-secondary" style="max-height: 65vh;"><code>
XXX
  ;
  $images->Identify();
  print <<XXX;
</code></pre>
    </div>
  </div>
</div>
XXX
  ;
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

  $tooltype=scalar $q->param('ToolType');
  View() unless defined($tooltype);
  Error('Unable to view image','no path is defined') unless $q->param('Path');
  RestoreQueryState(scalar $q->param('SessionID'),scalar $q->param('Path'),$tooltype);
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Resize image.
  #
  $image->Set(gravity=>scalar $q->param('Gravity'));
  $q->param('Geometry') =~ /(\d+)\D*(\d*)/;
  Error('Image area exceeds maximum allowable') if $1 && $2 &&
    (($1*$2) > (1024*$MaxImageArea));
  Error('Image area exceeds maximum allowable') if $1 && !$2 &&
    (($1*$1) > (1024*$MaxImageArea));
  $geometry='100%';
  $geometry=$q->param('Geometry') if $q->param('Geometry');
  $filter='Undefined';
  $filter=$q->param('FilterType') if $q->param('FilterType');
  $image->Set('filter:support'=>scalar $q->param('SupportFactor'))
    if $q->param('SupportFactor');
  $image->Set('filter:blur'=>scalar $q->param('BlurFactor'))
    if $q->param('BlurFactor');
  $status=$image->AdaptiveResize(geometry=>$geometry,filter=>$filter)
    if $q->param('Algorithm') eq 'adaptive resize *';
  $status=$image->LiquidRescale(geometry=>$geometry) if
    $q->param('Algorithm') eq 'liquid rescale *';
  $status=$image->Resize(geometry=>$geometry,filter=>$filter) if
    $q->param('Algorithm') eq 'resize *';
  $status=$image->Scale($geometry) if $q->param('Algorithm') eq 'scale *';
  $status=$image->Sample($geometry) if $q->param('Algorithm') eq 'sample *';
  $status=$image->Magnify() if $q->param('Algorithm') eq 'double size';
  $status=$image->Minify() if $q->param('Algorithm') eq 'half size';
  $status=$image->Extent(geometry=>$geometry,background=>
    $q->param('BackgroundColor')) if $q->param('Algorithm') eq 'extent *';
  $status=$image->Resample(density=>$geometry,filter=>$filter) if
    $q->param('Algorithm') eq 'resample *';
  $status=$image->Thumbnail($geometry) if $q->param('Algorithm') eq
    'thumbnail *';
  Error($status) if "$status";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  ($width,$height)=$image->Ping("$path/MagickStudio.mpc");
  $q->delete('Geometry');
  #
  # Display Resize form.
  #
  Header(GetTitle($image));
  print <<XXX;
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Resize Image</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Resize.html" target="help" class="text-decoration-none">resize</a> your image, specify dimensions and method (* requires parameter). Press <code>resize</code> to process.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'resize'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Geometry',-size=>25,-value=>"$width" . 'x' . "$height",-placeholder=>'Image Size'), "\n";
  print "<label for=\"Geometry\">Image Size</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Scaling Method</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Algorithm',-values=>@OptionTypes,-columns=>3,-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'resize'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Resize Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  
  my @filter_types=Image::Magick->QueryOption('filter');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Primitive',-values=>[@filter_types]), "\n";
  print "<label for=\"Primitive\">Filter</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SupportFactor',-size=>25,-value=>'0.0',-placeholder=>'Support'), "\n";
  print "<label for=\"SupportFactor\">Support</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BlurFactor',-size=>25,-value=>'1.0',-placeholder=>'Blur'), "\n";
  print "<label for=\"BlurFactor\">Blur</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3\">\n";
  my @gravity_types=Image::Magick->QueryOption('gravity');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Gravity',-values=>[@gravity_types]), "\n";
  print "<label for=\"Gravity\">Gravity</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BackgroundColor',-value=>'none',-size=>25,-placeholder=>'Background Color'), "\n";
  print "<label for=\"BackgroundColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Background Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  print DATA "image locator: ", scalar $q->param('URL'), "\n"
    if $q->param('URL');
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
    </main>

    <!-- Sidebar Column (~20% width on large screens) -->
    <aside class="col-lg-2 col-xl-2 px-3">
      <!-- Sponsor Card -->
      <div class="card im-card mb-4 overflow-hidden border-0 bg-gradient bg-primary bg-opacity-10">
        <div class="card-body p-3 text-center">
          <img src="https://imagemagick.org/image/wizard.jpg" alt="ImageMagick Wizard" class="rounded shadow mb-3 img-fluid" style="max-height: 200px;">
          <p class="small text-body-secondary mb-3">Help sustain the free ImageMagick online service.</p>
          <a href="https://github.com/sponsors/ImageMagick" target="_blank" rel="noopener" class="btn btn-sm btn-dark w-100 fw-semibold d-flex align-items-center justify-content-center gap-2">
            ❤️ Sponsor
          </a>
        </div>
      </div>
      <!-- Banner Ad Container -->
      <div class="my-4 text-center">
        <ins class="adsbygoogle"
          style="display:block"
          data-ad-client="ca-pub-3129977114552745"
          data-ad-slot="1083537442"
          data-ad-format="auto"
          data-full-width-responsive="true"></ins>
        <script>
          (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
      </div>
    </aside>
  </div>
</div>
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
  <footer class="mt-5 py-4 border-top bg-body-tertiary">
  <div class="container text-center">
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
      $path=Untaint(scalar $q->param('Path')) if $q->param('Path');
      $filename="$path/MagickStudio.gif";
      if (-e $filename)
        {
          ($width,$height)=$image->Ping("$filename" . '[0]');
          $url=substr($path,length($DocumentRoot));
          print "<div class=\"d-inline-block me-2 mb-3\">\n";
          print "<img alt=\"image icon\" src=\"$url/MagickStudio.gif\" ",
            "border=\"0\" width=\"$width\" height=\"$height\" ",
            "class=\"img-thumbnail shadow-sm\"/>\n</div>\n";
        }
      $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
        $q->param('SessionID') . '.gif';
      if (-e $filename)
        {
          ($width,$height)=$image->Ping("$filename" . '[0]');
          print "<div class=\"d-inline-block mb-3\">\n";
          print "<img alt=\"clipboard icon\" src=\"$DocumentDirectory/",
            "clipboard/", $q->param('SessionID'), ".gif\" border=\"0\" ",
            "width=\"$width\" height=\"$height\" ",
            "class=\"img-thumbnail shadow-sm\"/>\n</div>\n";
        }
    }
  print <<XXX;
    <div class="mb-2">
      <a href="#" class="text-decoration-none me-2">Back to top</a> •
      <a href="https://github.com/ImageMagick/ImageMagick/discussions" class="text-decoration-none mx-2">Community</a> •
    </div>
    <p class="text-secondary small mb-0">&copy; 1999 ImageMagick Studio LLC</p>
  </div>
  </footer>
  <!-- Javascript assets -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap\@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
XXX
  ;
  if ($Debug)
    {
      my($name);

      #
      # Display debugging information for an administrator.
      #
      print "<div class=\"card shadow-sm border-0 my-4 text-start\"><div class=\"card-body p-4\">\n";
      print "<h5 class=\"fw-bold mb-3\">CGI State Information</h5>\n";
      print "<ul class=\"list-group list-group-flush small\">\n";
      print "<li class=\"list-group-item\"><strong>Script:</strong> ", $0, "</li>\n";
      print "<li class=\"list-group-item\"><strong>Action:</strong> ", $action, "</li>\n";
      print "<li class=\"list-group-item\"><strong>Time:</strong> ", time-$timer, "s</li>\n";
      print "<li class=\"list-group-item\"><strong>Query state:</strong> <code>", $q->query_string, "</code></li>\n";
      print "</ul>\n";
      print "<div class=\"mt-3\">", $q->Dump, "</div>\n";
      print "<h6 class=\"fw-bold mt-4 mb-2\">Environment state</h6>\n";
      print "<ul class=\"list-unstyled small text-muted\">\n";
      print "<li><code>SponsorURL</code>: ", $SponsorURL, "</li>\n";
      print "<li><code>SponsorIcon</code>: ", $SponsorIcon, "</li>\n";
      print "<li><code>accept</code>: ", $q->Accept(), "</li>\n";
      print "<li><code>auth type</code>: ", $q->auth_type(), "</li>\n";
      print "<li><code>raw cookie</code>: ", $q->raw_cookie(), "</li>\n";
      print "<li><code>path info</code>: ", $q->path_info(), "</li>\n";
      print "<li><code>path translated</code>: ", $q->path_translated(), "</li>\n";
      print "<li><code>referer</code>: ", $q->referer(), "</li>\n";
      print "<li><code>local addr</code>: ", GetAddress($q->virtual_host()), "</li>\n";
      print "<li><code>remote addr</code>: ", $q->remote_addr(), "</li>\n";
      print "<li><code>remote ident</code>: ", $q->remote_ident(), "</li>\n";
      print "<li><code>remote host</code>: ", GetHostname($q->remote_host()), "</li>\n";
      print "<li><code>remote user</code>: ", $q->remote_user(), "</li>\n";
      print "<li><code>request method</code>: ", $q->request_method(), "</li>\n";
      print "<li><code>script name</code>: ", $q->script_name(), "</li>\n";
      print "<li><code>server name</code>: ", $q->server_name(), "</li>\n";
      print "<li><code>server software</code>: ", $q->server_software(), "</li>\n";
      print "<li><code>server port</code>: ", $q->server_port(), "</li>\n";
      print "<li><code>temporary directory</code>: ", $ENV{TMPDIR}, "</li>\n";
      print "<li><code>user agent</code>: ", $q->user_agent(), "</li>\n";
      print "<li><code>user name</code>: ", $q->user_name(), "</li>\n";
      print "<li><code>virtual host</code>: ", $q->virtual_host(), "</li>\n";
      print "<li><code>environment</code>: ", $q->http(), "</li>\n";
      print "<li><code>time stamp</code>: ", scalar(localtime), "</li>\n";
      print "</ul>\n";
      print "</div></div>\n";
    }
  print $q->end_html;
  die "FCGI_DONE\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
  $image=Image::Magick->new;
  $status=$image->Read("$path/MagickStudio.mpc");
  Error($status) if $#$image < 0;
  #
  # Transform image.
  #
  $parameter=$q->param('Parameter');
  $image->Set(fuzz=>scalar $q->param('Fuzz')) if $q->param('Fuzz');
  $image->Set(background=>scalar $q->param('BackgroundColor'));
  $image->Set(gravity=>scalar $q->param('Gravity'));
  $status=$image->AffineTransform([split(/[ ,]+/,$parameter)]) if
    $q->param('Option') eq 'affine *';
  $status=$image->AutoOrient() if $q->param('Option') eq 'auto-orient';
  $status=$image->Trim() if $q->param('Option') eq 'trim';
  $status=$image->Crop("$parameter") if $q->param('Option') eq 'crop *';
  $status=$image->Chop("$parameter") if $q->param('Option') eq 'chop *';
  $image=$image->Coalesce() if $q->param('Option') eq 'coalesce';
  $status=$image->Colorspace($q->param('Colorspace')) if
    $q->param('Option') eq 'colorspace';
  $status=$image->Deconstruct() if $q->param('Option') eq 'deconstruct';
  $status=$image->Deskew($parameter) if $q->param('Option') eq 'deskew';
  $status=$image=$image->Flatten() if $q->param('Option') eq 'flatten';
  $status=$image->Flop() if $q->param('Option') eq 'flop';
  $status=$image->Flip() if $q->param('Option') eq 'flip';
  $image=$image->Layers(method=>$q->param('LayerMethod')) if
    $q->param('Option') eq 'layers';
  $status=$image->Rotate(90) if $q->param('Option') eq 'rotate right';
  $status=$image->Rotate(-90) if $q->param('Option') eq 'rotate left';
  $color='none';
  $color=$q->param('BackgroundColor') if $q->param('BackgroundColor');
  $status=$image->Rotate(degrees=>$parameter,background=>$color) if
    $q->param('Option') eq 'rotate *';
  $status=$image->Shave("$parameter") if $q->param('Option') eq 'shave *';
  $status=$image->Shear("$parameter") if $q->param('Option') eq 'shear *';
  $status=$image->Splice("$parameter") if $q->param('Option') eq 'splice *';
  $status=$image->Roll("$parameter") if $q->param('Option') eq 'roll *';
  $image->Set(page=>'0x0+0+0') if $q->param('Repage') eq 'on';
  $status=$image->Transpose() if $q->param('Option') eq 'transpose';
  $status=$image->Transverse() if $q->param('Option') eq 'transverse';
  $status=$image->UniqueColors() if $q->param('Option') eq 'unique colors';
  Error($status) if "$status";
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Transform Image</h5>
    <p class="text-secondary mb-0">To <a href="$DocumentDirectory/Transform.html" target="help" class="text-decoration-none">transform</a> your image, specify the method and supply parameters if required (*). Press <code>transform</code> to continue.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'resize'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Parameter',-size=>25,-placeholder=>'Parameter'), "\n";
  print "<label for=\"Parameter\">Parameter</label>\n";
  print "</div>\n";

  print "<div class=\"mb-4\">\n";
  print "<label class=\"fw-bold mb-2\">Choose Transform</label>\n";
  print "<div class=\"row g-2\">\n";
  print $q->radio_group(-name=>'Option',-values=>@OptionTypes,-columns=>3,-default=>'trim',-class=>'form-check-input'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'transform'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Transform Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,-value=>'0%',-placeholder=>'Fuzz'), "\n";
  print "<label for=\"Fuzz\"><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\" class=\"text-decoration-none\">Fuzz</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  my @gravity_types=Image::Magick->QueryOption('gravity');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Gravity',-values=>[@gravity_types]), "\n";
  print "<label for=\"Gravity\">Gravity</label>\n";
  print "</div>\n";
  print "</div>\n";

  my @colorspace_types=Image::Magick->QueryOption('colorspace');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Colorspace',-values=>[@colorspace_types],-default=>'sRGB'), "\n";
  print "<label for=\"Colorspace\"><a href=\"$DocumentDirectory/Colorspace.html\" target=\"help\" class=\"text-decoration-none\">Colorspace</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3 mb-3\">\n";
  my @layer_types=Image::Magick->QueryOption('layers');
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'LayerMethod',-values=>[@layer_types],-default=>'Optimize'), "\n";
  print "<label for=\"LayerMethod\">Layer Method</label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BackgroundColor',-value=>'none',-size=>25,-placeholder=>'Background Color'), "\n";
  print "<label for=\"BackgroundColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Background Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"mt-3\">\n";
  print "<h6 class=\"fw-bold mb-3\">Miscellaneous options</h6>\n";
  print "<div class=\"form-check\">\n";
  print $q->checkbox(-class=>'form-check-input',-name=>'Repage',-checked=>'true',-label=>' Reset page geometry.'), "\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
    if ($q->param('Format') && (scalar $q->param('Format') ne 'Implicit'));
  $scene='';
  $scene='[' . scalar $q->param('Scene') . ']' if $q->param('Scene');
  $image=Image::Magick->new;
  $image->Set(font=>$DefaultFont);
  $image->Set(density=>scalar $q->param('Density')) if $q->param('Density');
  $image->Set(size=>scalar $q->param('SizeGeometry')) if
    $q->param('SizeGeometry');
  if ($q->param('File'))
    {
      #
      # Copy data file to workarea.
      #
      $filename=Untaint(scalar $q->param('File'));
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
          $filename=Untaint(scalar $q->param('URL'));
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
              $filename=Untaint(scalar $q->param('Meta'));
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
  $image->Set(density=>scalar $q->param('Density')) if $q->param('Density');
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
  $basename=scalar $filename;
  $filename=~/^((?:.*[:\\\/])?)(.*)(\..*)/s;
  $basename=$2 if $2;
  $basename=~s/ //g;
  $basename=~s/#//g;
  $q->param(-name=>'Name',-value=>$basename);
  $magick=~tr/A-Z/a-z/;
  $q->param(-name=>'Magick',-value=>$magick);
  $digest=Digest::SHA3->new(512);
  $digest->add($HashDigestSalt,$image->Get('signature'),scalar $filename,
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
      sleep $load_average/2;
      print $q->redirect($RedirectURL);
      die "FCGI_DONE\n";
    }
  $url=$q->script_name();
  $q->delete('ToolType');
  $q->param(-name=>'ToolType',-value=>'Upload');
  Header("Magick Online Studio");
  print <<XXX;
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h4 class="card-title fw-bold mb-3">Welcome to Magick Online Studio</h4>
    <p class="card-text text-secondary lead">Select an image from your device or supply a URL. Adjust processing attributes below and click <span class="fw-bold">View</span> to start editing or converting.</p>
  </div>
</div>
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
  print $q->start_multipart_form(-action=>$action,-method=>'POST');
  print $q->hidden(-name=>'SessionID'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"mb-3\">\n";
  print "<label class=\"form-label fw-bold\"><a href=\"$DocumentDirectory/Filename.html\" target=\"help\" class=\"text-decoration-none\">Filename</a></label>\n";
  print $q->filefield(-class=>'form-control',-name=>'File',-size=>50,-maxlength=>1024), "\n";
  print "</div>\n";

  print "<div class=\"form-floating mb-3\">\n";
  print $q->textfield(-class=>'form-control',-name=>'URL',-size=>50,-placeholder=>'URL'), "\n";
  print "<label for=\"URL\"><a href=\"$DocumentDirectory/URL.html\" target=\"help\" class=\"text-decoration-none\">URL</a></label>\n";
  print "</div>\n";

  $filename=$DocumentRoot . $DocumentDirectory . '/clipboard/' .
    $q->param('SessionID')  . '.mpc';
  if ((-e $filename) && defined($q->param('SessionID')))
    {
      print "<div class=\"form-check mb-3\">\n";
      print $q->checkbox(-class=>'form-check-input',-name=>'Append',-label=>' Append to clipboard image.'), "\n";
      print "</div>\n";
    }

  print "<div class=\"d-flex gap-2 pt-2\">\n";
  print $q->submit(-name=>'Action',-class=>'btn btn-primary px-4 py-2 fw-semibold shadow-sm',-value=>'view'), "\n";
  print $q->reset(-name=>'reset',-class=>'btn btn-outline-secondary px-4 py-2',-value=>'Reset Form'), "\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print <<XXX;
<div class="alert alert-secondary shadow-sm border-0 mb-4">
  An example <a href="$url?URL=$ExampleImage;Action=view" class="alert-link">image</a> is available to explore features of <code>Magick Online Studio</code>, version $version.
</div>

<div class="row g-4 mb-4">
  <div class="col-md-6">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-body-tertiary fw-bold border-0 py-3 px-4">Privacy Notice</div>
      <div class="card-body p-4 text-secondary">
        <p class="card-text mb-0">Your privacy is safeguarded. Uploaded images are stored temporarily on secure local servers for processing and deleted automatically within a few hours. Images are accessible only to you.</p>
      </div>
    </div>
  </div>
  <div class="col-md-6">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-body-tertiary fw-bold border-0 py-3 px-4">Liability Notice</div>
      <div class="card-body p-4 text-secondary">
        <p class="card-text mb-0">By using this service, you agree that ImageMagick Studio LLC is not liable for data loss or privacy issues. Use of this service is at your own risk. Ensure uploaded content complies with applicable laws.</p>
      </div>
    </div>
  </div>
</div>

<div class="card shadow-sm border-0 mb-4">
  <div class="card-header bg-body-tertiary fw-bold border-0 py-3 px-4">Upload Properties</div>
  <div class="card-body p-4">
    <p class="text-secondary mb-4">Optional parameters for frame selection or raw formats (RGB, GRAY).</p>
XXX
  ;
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'SizeGeometry',-size=>25,-value=>'320x240',-placeholder=>'Size'), "\n";
  print "<label for=\"SizeGeometry\"><a href=\"$DocumentDirectory/Size.html\" target=\"help\" class=\"text-decoration-none\">Size</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Format',-values=>[@UploadTypes]), "\n";
  print "<label for=\"Format\"><a href=\"$DocumentDirectory/Format.html\" target=\"help\" class=\"text-decoration-none\">Format</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  my @interlace_types=Image::Magick->QueryOption('interlace');
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Meta',-size=>25,-value=>'white',-placeholder=>'Meta'), "\n";
  print "<label for=\"Meta\"><a href=\"$DocumentDirectory/Meta.html\" target=\"help\" class=\"text-decoration-none\">Meta</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Interlace',-values=>[@interlace_types],-default=>'None'), "\n";
  print "<label for=\"Interlace\"><a href=\"$DocumentDirectory/Interlace.html\" target=\"help\" class=\"text-decoration-none\">Interlace</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  my @channels=Image::Magick->QueryOption('channel');
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Scene',-size=>25,-placeholder=>'Scene'), "\n";
  print "<label for=\"Scene\"><a href=\"$DocumentDirectory/Scene.html\" target=\"help\" class=\"text-decoration-none\">Scene</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Channel',-values=>[@channels],-default=>'All'), "\n";
  print "<label for=\"Channel\"><a href=\"$DocumentDirectory/Channel.html\" target=\"help\" class=\"text-decoration-none\">Channel</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Passphrase',-size=>25,-placeholder=>'Passphrase'), "\n";
  print "<label for=\"Passphrase\"><a href=\"$DocumentDirectory/Passphrase.html\" target=\"help\" class=\"text-decoration-none\">Passphrase</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Density',-size=>8,-value=>90,-placeholder=>'Density'), "\n";
  print "<label for=\"Density\">Density</label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
      $status=$image->Draw(primitive=>$primitive,points=>$points,fill=>$fill,
        bordercolor=>$bordercolor,method=>$method);
      Error($status) if "$status";
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
  $path=Untaint(scalar $q->param('Path'));
  chdir($path) || Error('Your image has expired',$q->Param('Name'));
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
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-2">Image Canvas</h5>
    <p class="text-secondary mb-0">Select navigation tabs above to edit, transform, or save your image. Click directly on the canvas to paint using the parameters below. See <a href="https://imagemagick.org/" class="text-decoration-none">ImageMagick</a> for documentation.</p>
  </div>
</div>
XXX
  ;
  print $q->start_form(-method=>'POST');
  print $q->hidden(-name=>'CacheID'), "\n";
  print $q->hidden(-name=>'SessionID'), "\n";
  print $q->hidden(-name=>'Path'), "\n";
  print $q->hidden(-name=>'ToolType'), "\n";
  print $q->hidden(-name=>'Name'), "\n";
  print $q->hidden(-name=>'Magick'), "\n";
  print $q->hidden(-name=>'Action',-class=>'btn btn-primary',-value=>'view'), "\n";
  
  print "<div class=\"card shadow-sm border-0 mb-4 text-center\">\n";
  print "<div class=\"card-body p-3\">\n";
  print $q->image_button(-class=>'img-fluid rounded border shadow-sm mx-auto d-block',-name=>$basename,
    -src=>"$url/$basename.$format",-border=>0,-width=>$width,-height=>$height,
    -style=>"cursor:crosshair"), "\n";
  
  if (defined($q->param("$basename.x")) || defined($q->param("$basename.y")))
    {
      my $width=$coalesce->Get('columns');
      my $height=$coalesce->Get('rows');
      my $x=$q->param("$basename.x");
      my $y=$q->param("$basename.y");
      print "<div class=\"bg-body-tertiary rounded border p-2 mt-3 d-inline-block text-start small\"><samp>$x,$y: ";
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
      print "</samp></div>\n";
    }
  if ($image->Get('error') != 0.0)
    {
      my $error=$image->Get('error');
      $error*=(Image::Magick->QuantumRange);
      print "<div class=\"bg-body-tertiary rounded border p-2 mt-2 d-inline-block text-start small\"><samp>";
      print 'Distortion: ' . $error . ' (' . $image->Get('error') . ')';
      print "</samp></div>\n";
    }
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"card shadow-sm border-0 mb-4\">\n";
  print "<div class=\"card-header bg-body-tertiary fw-bold border-0 py-3 px-4\">Paint Properties</div>\n";
  print "<div class=\"card-body p-4\">\n";
  print "<div class=\"row g-3 mb-3\">\n";
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Fuzz',-size=>25,-value=>'0%',-placeholder=>'Fuzz'), "\n";
  print "<label for=\"Fuzz\"><a href=\"$DocumentDirectory/Fuzz.html\" target=\"help\" class=\"text-decoration-none\">Fuzz</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  my @method_types=Image::Magick->QueryOption('method');
  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Method',-values=>[@method_types]), "\n";
  print "<label for=\"Method\"><a href=\"$DocumentDirectory/Paint.html\" target=\"help\" class=\"text-decoration-none\">Method</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-4\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->popup_menu(-class=>'form-select',-name=>'Primitive',-values=>[@PrimitiveTypes]), "\n";
  print "<label for=\"Primitive\"><a href=\"$DocumentDirectory/Paint.html\" target=\"help\" class=\"text-decoration-none\">Paint Type</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"row g-3\">\n";
  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'Color',-value=>'none',-size=>25,-placeholder=>'Fill Color'), "\n";
  print "<label for=\"Color\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Fill Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";

  print "<div class=\"col-md-6\">\n";
  print "<div class=\"form-floating\">\n";
  print $q->textfield(-class=>'form-control',-name=>'BorderColor',-value=>'none',-size=>25,-placeholder=>'Border Color'), "\n";
  print "<label for=\"BorderColor\"><a href=\"$DocumentDirectory/Color.html\" target=\"help\" class=\"text-decoration-none\">Border Color</a></label>\n";
  print "</div>\n";
  print "</div>\n";
  print "</div>\n";

  print "</div>\n";
  print "</div>\n";
  print $q->end_form, "\n";
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
<div class="card border-warning shadow-sm mb-4">
  <div class="card-body p-4 text-center">
    <div class="text-warning mb-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-exclamation-triangle-fill" viewBox="0 0 16 16">
        <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
      </svg>
    </div>
    <h4 class="card-title text-warning fw-bold mb-2">$message</h4>
    <p class="card-text text-secondary mb-3">$qualifier</p>
    <p class="text-secondary mb-0">Select a menu item above to continue.</p>
  </div>
</div>
XXX
  ;
  Trailer(1);
  die $message;
}

#
# FastCGI request loop.  Each pass through this loop services exactly one
# HTTP request; the Perl process itself stays resident between requests.
#
#setpriority(0,0,getpriority(0,0)+4);  # be nice
$CGI::POST_MAX=1024*$MaxFilesize;
our ($image, $compare, $composite);
my $MAX_REQUESTS  = 200; 
my $request_count = 0;
while ($q = CGI::Fast->new)
{
  $request_count++;
  last if $request_count >= $MAX_REQUESTS;
  eval
  {
    $timer=time;
    %seen=();
    $header=undef;
    $action=undef;
    $q->autoEscape(undef);
    $q->delete('CacheID');
    $q->param(-name=>'CacheID',-value=>rand($timer+$$));
    #
    # Choose function as determined by the query and environment.
    #
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
  };
  undef $image;
  undef $compare;
  undef $composite;
  $q=undef;
  if ($@ && $@ !~ /^FCGI_DONE/)
    {
      #
      # An unexpected error escaped our own Error()/Warning() handling.
      # Log it and move on to the next request instead of letting it
      # kill the persistent worker.
      #
      warn "MagickStudio request error: $@";
    }
}
