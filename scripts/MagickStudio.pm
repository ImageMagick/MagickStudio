use strict;
use warnings;

our $AreaLimit = "128MB";  # image area limit
our $ContactInfo = 'magick-users@imagemagick.org';
our $Debug = undef;  # no debugging by default
our $DefaultFont = "Arial";
our $DiskLimit = "1.5GB";  # disk limit
our $DocumentDirectory = '/MagickStudio';  # relative to server root
our $DocumentRoot = '/var/www/html/ImageMagick';  # server root
our $ExpireCache = '+1h';  # when to expire browser cache
our $ExpireThreshold = 8*3600;  # work files time to live
our $IconSize = '80x80>';
our $LoadAverageThreshold = 10.0;  # suspend service if load average exceeds threshold
our $MapLimit = "512MB";  # map limit
our $MaxFilesize = 4096;  # max file size in kilobytes
our $MaxImageArea = 16384;  # max image area in kilobytes (width*height)
our $MaxImageExtent = 16384;  # max image extent in kilobytes (width*height*frames)
our $ThreadLimit = 2;  # max number of worker threads
our $MaxWorkFiles = 8192;  # max number of work files
our $MemoryLimit = "256MB";  # memory limit
our $MinExpireAge = 7200;  # minimum expire age
our $RedirectURL = "http://studio.webbyland.com/MagickStudio/scripts/MagickStudio.cgi";
our $SponsorIcon = "networkredux.png";
our $SponsorURL = "http://www.networkredux.com/";
our $TimeLimit = 120;  # time limit to stop runaway jobs
our $Timeout = 120;  # timeout value for uploading an image
1; 
