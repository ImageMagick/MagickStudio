use strict;
use warnings;

our $ContactInfo = 'magick-users@imagemagick.org';
our $Debug = undef;  # no debugging by default
our $DefaultFont = "Arial";
our $DocumentDirectory = '/MagickStudio';  # relative to server root
our $DocumentRoot = '/var/www/html/ImageMagick';  # server root
our $ExampleImage = 'https://archive.imagemagick.org/image/wizard.jpg';
our $ExpireCache = '+1h';  # when to expire browser cache
our $ExpireThreshold = 8*3600;  # work files time to live
our $IconSize = '100x100>';
our $LoadAverageThreshold = 10.0;  # redirect service if load average exceeds threshold
our $MaxFilesize = 8192;  # max file size in kilobytes
our $MaxImageArea = 16384;  # max image area in kilobytes (width*height)
our $MaxImageExtent = 16384;  # max image extent in kilobytes (width*height*frames)
our $MaxWorkFiles = 4096;  # max number of work files
our $MinExpireAge = 7200;  # minimum expire age
our $RedirectURL = "https://warrior.imagemagick.org/MagickStudio/";
our $SponsorIcon = "networkredux.png";
our $SponsorURL = "http://www.networkredux.com/";
our $Timeout = 120;  # timeout value for uploading an image
1; 
