# Hackabot utilities for external Perl hooks and commands

package Hackabot::Client;

use strict;
use warnings;

use DBI;
use XML::Simple;
use IO::Handle;
use Socket;

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

sub connect {
    my $self = shift;

    my $conn;
    my $addr = sockaddr_un($ENV{'HB_ROOT'}."/sock");

    # Not good to die in a module, but whatever
    socket($conn,PF_UNIX,SOCK_STREAM,0) or die "Unable to create a socket!";
    connect($conn, $addr) or die "Unable to Connect to $addr";
    $conn->autoflush(1);

    $self->{'conn'} = $conn;
}

sub close {
    my $self = shift;

    close $self->{'conn'};
}

sub cmd {
    my ($self, $send) = @_;

    if (not defined($self->{'conn'})) {
        $self->connect;
    }

    my $conn = $self->{'conn'};
    print $conn "$send\n";
    my $ret = <$conn>;

    if (not defined $ret) {
        $ret = "error connection lost with no result";
    }
    return $ret;
}

sub readall {
    my $msg = "";
    while (<>) {
        $msg .= $_;
    }

    chomp $msg;
    return $msg;
}

sub readline {
    my $line = <>;
    if (not defined $line) {
        $line = "";
    }

    chomp $line;
    return $line;
}

sub private {
    if (defined $ENV{'HBEV_PRIVATE'} and $ENV{'HBEV_PRIVATE'} eq "True") {
        return 1;
    }
    else {
        return 0;
    }
}

sub sent_by {
    if defined $ENV{'HBEV_SENT_BY'} {
        return $ENV{'HBEV_SENT_BY'};
    }
    else {
        return "";
    }
}

sub sent_to {
    if defined $ENV{'HBEV_SENT_TO'} {
        return $ENV{'HBEV_SENT_TO'};
    }
    else {
        return "";
    }
}

sub channel {
    if (private()) {
        return undef;
    }
    else {
        return sent_to();
    }
}

1;
