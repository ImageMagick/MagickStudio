use strict;
use warnings;

our $AreaLimit = "64mb";  # image area limit
our $ContactInfo = 'magick-users@imagemagick.org';
our $Debug = undef;  # no debugging by default
our $DefaultFont = "Arial";
our $DiskLimit = "1gb";  # disk limit
our $DocumentDirectory = '/MagickStudio';  # relative to server root
our $DocumentRoot = '/var/www/html/ImageMagick';  # server root
our $ExpireCache = '+1h';  # when to expire browser cache
our $ExpireThreshold = 4*3600;  # work files time to live
our $IconSize = '80x80>';
our $LoadAverageThreshold = 10.0;  # redirect service if load average exceeds threshold
our $MapLimit = "64mb";  # map limit
our $MaxFilesize = 3072;  # max file size in kilobytes
our $MaxImageArea = 3072;  # max image area in kilobytes (width*height)
our $MaxImageExtent = 6144;  # max image extent in kilobytes (width*height*frames)
our $MaxWorkFiles = 4096;  # max number of work files
our $MemoryLimit = "32mb";  # memory limit
our $MinExpireAge = 3600;  # minimum expire age
our $RedirectURL = "http://www.imagemagick.org/MagickStudio/scripts/MagickStudio.cgi";  # redirect URL
our $SponsorIcon = "sponsor.png";  # sponsor icon
our $SponsorURL = "http://www.imagemagick.org";  # sponsor url
our $Timeout = 60;  # timeout value for uploading an image
1; 
