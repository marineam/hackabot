# Hackabot utilities for external Perl hooks and commands

package Hackabot::Client;

use strict;
use warnings;

use DBI;
use XML::Simple;

sub new {
    my $class = shift;
    my $self = bless({}, $class);

    $self->{'conf'} = XMLin($ENV{'HB_XML'});

    return $self;
}

sub dbi {
    my $self = shift;

    my $dbhost = $self->{'conf'}->{'database'}->{'hostname'};
    my $dbname = $self->{'conf'}->{'database'}->{'database'};
    my $dbuser = $self->{'conf'}->{'database'}->{'username'};
    my $dbpass = $self->{'conf'}->{'database'}->{'password'};

    return DBI->connect("DBI:mysql:$dbname:$dbhost",
        $dbuser, $dbpass, { PrintError => 1 });
}

1;
