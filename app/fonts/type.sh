#!/usr/bin/perl -w
#
use strict;
(my $prog = $0) =~ s/^.*\///;
sub Usage {
  die @_, &herefile( qq{
    | Usage: $prog > ~/.magick/type.xml
    |
    | Generate an ImageMagick font list "type.xml" file for ALL fonts (both
    | true type fonts (ttf) and Ghostscript fonts (afm))  currently on the
    | local linux system.  The fonts are found using the linux "locate"
    | command, and the output informs IM of their location, font type, name
    | and family.
    |
    | When the file has been generated you can then see a list of the
    | fonts found with...
    |    convert -list type
    | And use the fonts, by name, with commands like...
    |    convert -font Candice -pointsize 72 label:Anthony  x:
    | Instead of specifying the specific TTF font file
    |    convert -font ~/lib/font/truetype/favoriate/candice.ttf \
    |            -pointsize 72 label:Anthony  x:
    |
    | NOTE before IM v6.1.2-3  the font list file was called "type.mgk" and
    | not "type.xml".
    |
    | Note: IM version 5.5.7 installed as a system program (such as from a
    | linux RPM) will NOT read this file from the home directory location
    | above automatically.  To fix this you may need to add a line to the
    | systems "type.mgk" file such as...
    |    <include file="../../../../../../../home/anthony/.magick/type.mgk"/>
    | Note that the path must be a relative path, thus the numerious ".."
    | in the above line, you can specify more ".." than you really need.
    |
    |  Anthony Thyssen  May 2003
  });
}
# Internal working notes...
#
# This script requires the linux "locate" command to find the fonts.
# originally it needed an extrenal tool to read TTF fonts, but now
# that is built-in.
#
# WARNING: Input arguments are NOT tested for correctness.
# This script represents a security risk if used ONLINE.
# I accept no responsiblity for misuse. Use at own risk.
#
# The original version of this hack script was found on
#   http://studio.imagemagick.org/pipermail/magick-users/2003-March/001703.html
# by  raptor <raptor@unacs.bg>, presumaibly around  March 2002
#
# Re-Write by Anthony Thyssen <anthony@cit.gu.edu.au>, August 2002
# May 2003   Update with TTF family names
# Oct 2005   Update to use "getttinfo" is available
#
use strict;
use Fcntl qw( O_RDONLY SEEK_SET );
binmode(STDOUT, ":utf8");
binmode(STDERR, ":utf8");

my $VERBOSE = 1; # verbose output of fonts found
my $DEBUG   = 0; # debug TTF file decoding

# ======================================================================
# Subroutines...
# ======================================================================
#
# True Type fonts Handling
#
my $ttf_template = herefile( q{
  |   <type
  |      format="ttf"
  |      name="%s"
  |      glyphs="%s"
  |      />
  });
my $ttf_template_full = herefile( q{
  |   <type
  |      format="ttf"
  |      name="%s"
  |      fullname="%s"
  |      family="%s"
  |      glyphs="%s"
  |      />
  });

sub ttf_file_parse {
  #
  # Method for Parsing TTF files curtesy of
  #     Peter N Lewis <peter@stairways.com.au>
  #
  my $file = $_[0];
  my ( $font_family, $font_fullname, $font_psname ) = ( '','','','' );

  my ( $fh, $len );
  unless ( sysopen( $fh, $file, O_RDONLY ) ) {
    warn "Cannot open $file: $!\n";
    return;
  }
  my $header;
  unless ( sysread( $fh, $header, 12 ) ) {
    warn "Cant read header: $file";
    close($fh);
    return;
  }
  my ( $sfnt_version, $numTables, $searchRange, $entrySelector, $rangeShift
     ) = unpack( 'Nnnnn', $header );

  my $sfnt_version_code = unpack( 'A4', $header );
  unless (  $sfnt_version == 0x00010000
         || $sfnt_version_code eq 'true'
         || $sfnt_version_code eq 'typ1' ) {
    warn "TTF Version mismatch, not a basic TrueType font file: $file";
    close($fh);
    return;
  }

  #print STDERR "TTF Table count: $numTables\n" if $DEBUG;
  foreach ( 1..$numTables ) {
    my $table_entry;
    unless ( sysread( $fh, $table_entry, 16 ) ) {
      warn "Cant read master table $_ from $file";
      last;
    }

    my ( $table_tag, $table_checkSum, $table_offset, $table_length
       ) = unpack( 'A4NNN', $table_entry );
    #print STDERR "Table: $table_tag\n" if $DEBUG;
    $table_tag eq 'name' or next;

    my $table_header;
    sysseek( $fh, $table_offset, SEEK_SET ) or die "Can't seek: $file";
    sysread( $fh, $table_header, 6 );
    my ( $table_format, $table_count, $table_stringOffset
       ) = unpack( 'nnn', $table_header );
    print STDERR "Name Table Entries: $table_count\n" if $DEBUG;
    my $table_base = $table_offset + 6;
    my $storage_base = $table_base + $table_count * 12;

    foreach my $index ( 1..$table_count ) {
      my $entry;
      sysseek( $fh, $table_base + ($index-1)*12, SEEK_SET )
          or die "Cant seek: $file";
      sysread( $fh, $entry, 12 );
      my ( $name_platformID, $name_encodingID, $name_languageID,
           $name_id, $name_length, $name_offset
         ) = unpack( 'nnnnnn', $entry );
      print STDERR "Index[$index]: ", join ( ", ",
              $name_platformID, $name_encodingID, $name_languageID,
              $name_id, $name_length, $name_offset ), "\n" if $DEBUG;
      #
      # ID meanings : figured out from getttinfo
      #
      # Platform: 0=Apple  1=macintosh  3=microsoft
      # Encoding: 0=unicode(8) 1=unicode(16)
      # Language: 0=english  1033=English-US  1041=Japanese 2052=Chinese
      #
      next unless $name_languageID == 0
               || $name_languageID == 1033
               ;

      my $name;
      sysseek( $fh, $storage_base + $name_offset, SEEK_SET )
            or die "Cant seek: $file";
      sysread( $fh, $name, $name_length );

      # Decode UTF-16 to UTF-8 if nessary
      $name = pack("U*",unpack("n*", $name)) if $name_encodingID == 1;
      $name =~ s/\0//g;   # clean fonts use UTF-16 when it should be UTF-8
      print STDERR "$name\n" if $DEBUG;

      $font_family = $name       if $name_id == 1;
      #font_subfamily = $name    if $name_id == 2;  # (EG: Regular)
      #font_identifier = $name   if $name_id == 3;  # Unique Name
      $font_fullname = $name     if $name_id == 4;
      #font_version = $name      if $name_id == 5;
      $font_psname = $name       if $name_id == 6;  # Postscipt Name
      #font_trademark = $name    if $name_id == 7;
      #font_manufacturer = $name if $name_id == 8;
      #font_designer = $name     if $name_id == 9;
    }
    last;  # found "name" table -- skip any other tables as irrelevent
  }
  close( $fh );
  return ( $font_family, $font_fullname, $font_psname );
}

sub ttf_name {
  my $file = shift;

  my ( $family, $fullname, $psname ) = &ttf_file_parse( $file );
  print STDERR "$file\n\t==> $family -- $fullname -- $psname\n" if $DEBUG;

  $fullname =~ s/[^\s\w-]//g;        # Check: Pepsi.ttf
  $fullname =~ s/^\s+//;
  $fullname =~ s/\s+$//;
  $fullname =~ s/(^|\s)-/$1/g;
  $fullname =~ s/-(\s|$)/$1/g;

  $family   =~ s/[^\s\w-]//g;        # Check: Pepsi.ttf
  $family   =~ s/^\s*//;
  $family   =~ s/\s*$//;
  $family   =~ s/\s*(MS|ITC)$//;     # font factory ititials
  $family   =~ s/^(MS|ITC)\s*//;
  $family   =~ s/\s*(FB|MT)\s*/ /;   # Check: MaturaScriptCapitals
  $family   =~ s/^Monotype\s*//;     # Check: Corsiva
  $family   =~ s/^AR PL\s*//;        # Check: gkai00mp.ttf

  # Determine simple font name 
  #   Junk/abbr decriptive strings, foundaries, etc
  #   Test with the fonts given
  my $name = ($fullname);
  $name =~ s/-/ /g;
  $name   =~ s/\s*(MS|ITC)$//;  # font factory ititials
  $name   =~ s/^(MS|ITC)\s*//;
  $name   =~ s/\s*(FB|MT)\s*/ /;   # Check: MaturaScriptCapitals
  $name   =~ s/^Monotype\s*//;     # Check: Corsiva
  $name   =~ s/^AR PL\s*//;         # Check: gkai00mp.ttf

  $name =~ s/Regular//g;                # Check: Gecko
  $name =~ s/\bReg\b//g;                # Check: agencyr.ttf
  $name =~ s/\bNormal\b//g;
  #$name =~ s/\bSans\b//g;
  $name =~ s/\bDemi\s*[Bb]old\b/Db/g;
  $name =~ s/\bCondensed\b/C/g;
  $name =~ s/\bBold\b/B/g;
  $name =~ s/\bItalic\b/I/g;
  $name =~ s/\bExtra[Bb]old\b/Xb/g;
  $name =~ s/\bBlack\b/Bk/g;
  $name =~ s/\bHeavy\b/H/g;
  $name =~ s/\bMedium\b/M/g;            # Check: gkai00mp.ttf
  $name =~ s/\bLight\b/L/g;
  $name =~ s/\bOblique\b/Ob/g;

  $name =~ s/\s+//g;

  $fullname =~ s/\s+/ /g;
  $fullname =~ s/\s$//;
  $fullname =~ s/^\s//;

  # Failed to parse TTF file?
  return( ( $file =~ m/^.*\/(.*?).ttf$/ )[0] ) unless $name;

  return ($name, $fullname, $family);  # return the name if found!
}

sub do_ttf_fonts {
  for my $file ( locate('.ttf') ) {
    chop $file;
    my (@ttf) = ttf_name($file);

    print STDERR join( ' - ', @ttf), "\n"  if $VERBOSE;
    printf $ttf_template, @ttf, $file       if @ttf == 1;
    printf $ttf_template_full, @ttf, $file  if @ttf == 3;
  }
}


#---------------------------
#
# Adobe Type fonts
#
# Get font name from the AFM file
my $afm_template_full = herefile( q{
  |   <type
  |      format="type1"
  |      name="%s"
  |      fullname="%s"
  |      family="%s"
  |      glyphs="%s"
  |      metrics="%s"
  |      />
  });

sub afm_name {
  my $file = shift;

  my( $name, $fullname, $family ) = ('','','');
  if ( open AFM, $file ) {
    while( <AFM> ) {
      chop; last if /^StartCharMetrics/;
      #$name     = $1  if /^FontName (.*)/;
      $fullname = $1  if /^FullName (.*)/;
      $family   = $1  if /^FamilyName (.*)/;
    }
    close AFM;

    $family =~ s/\s*L$//;    # just the stupid 'L'
    $fullname =~ s/\bL\b//;

    $name = $fullname;

    $name =~ s/\bRegular\b//;            # Junk/abbr decriptive strings
    $name =~ s/\bDemi\s*[Bb]old\b/Db/g;
    $name =~ s/\bCondensed\b/C/g;
    $name =~ s/\bBold\b/B/g;
    $name =~ s/\bItalic\b/I/g;
    $name =~ s/\bExtra[Bb]old\b/Xb/g;
    $name =~ s/\bBlack\b/Bk/g;
    $name =~ s/\bHeavy\b/H/g;
    $name =~ s/\bLight\b/L/g;

    $name =~ s/[-\s]+//g;
    $fullname =~ s/\s+/ /g;
    $fullname =~ s/\s$//g;
    $fullname =~ s/^\s//g;
  } else {
    warn "Cannot open $file";
  }

  return ($name, $fullname, $family ) if $name && $fullname && $family;
}

sub do_afm_fonts {
  my %atf;
  # locate abode font files
  map { chop; my ($k) = m/^(.*?).pfb*$/; $atf{$k}{pfb} = $_ } locate('.pfb');
  map { chop; my ($k) = m/^(.*?).afm*$/; $atf{$k}{afm} = $_ } locate('.afm');

  # for each Abode font where BOTH files were found.
  for my $key (keys %atf) {
    next unless $atf{$key}{pfb} && $atf{$key}{afm};
    my (@afm) = afm_name($atf{$key}{afm});

    print STDERR join( ' - ', @afm), "\n"   if $VERBOSE;
    printf $afm_template_full, @afm, $atf{$key}{pfb}, $atf{$key}{afm}
                                                         if @afm == 3;
  }
}

# -----------------------------
#
#  Miscellanous functions
#
sub locate {
  #return `locate -r $_[0]\$`;
  return `locate $_[0] | grep $_[0]\$`;
}

sub herefile {  # Handle a multi-line quoted indented string
  my $string = shift;
  $string =~ s/^\s*//;        # remove start spaces
  $string =~ s/^\s*\| ?//gm;  # remove line starts
  $string =~ s/\s*$/\n/g;     # remove end spaces
  return $string;
}

# ======================================================================
# Main Function
# ======================================================================


# HACK -- extract font names for the given TTF font file.
if ( @ARGV ) {
  $DEBUG=1,shift if $ARGV[0] =~ /^-d$/i;
  Usage     unless $ARGV[0] =~ /\.ttf$/i;
  for my $file ( @ARGV ) {
    print join( ' - ', ttf_name($file) ), "\n";
  }
  exit 0;
}

# Generate the "type.xml" file.

# Do the job...
print herefile( q{
  | <?xml version="1.0"?>
  | <typemap>
});

print STDERR "Doing TTF fonts\n" if $VERBOSE;
do_ttf_fonts();
print STDERR "Doing ATM fonts\n" if $VERBOSE;
do_afm_fonts();

print "</typemap>\n";


