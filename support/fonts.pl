#!/usr/local/bin/perl
# MagickStudio.
#
# cristy@dupont.com, September 1996.
#
use Image::Magick;
use strict;

my($command, $file, $font, @fonts, $image, $pointsize, $string);

#
# Create font tiles.
#
umask(002);
mkdir('.fonts');
system('/bin/cp .webmagickrc .fonts');
chdir('.fonts');
$image=new Image::Magick;
@fonts=$image->QueryFont();
foreach (@fonts)
{
  $font=$_;
  $image=Image::Magick->new(font=>$font,pointsize=>24);;
  $image->Read("label:$font");
  $image->Trim();
  $image->Write("$font.gif");
  print "$font ", $image->Get('width'), 'x', $image->Get('height'), "\n";
}
#
# Create web index.
#
system("webmagick -verbose");
system('/bin/mv -f .index* * ../../fonts');
system('/bin/rm -rf ../.fonts');
