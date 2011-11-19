# Hackabot utilities for external Perl hooks and commands

package Hackabot::Client;

use strict;
use warnings;

use DBI;
use XML::Simple;
use Time::Piece;
use IO::Handle;
use Socket;

sub new {
    my $class = shift;
    my $self = bless({}, $class);

    if (defined $ENV{'HB_XML'}) {
        $self->{'conf'} = XMLin($ENV{'HB_XML'}, @_);
    }
    else {
        $self->{'conf'} = {};
    }

    return $self;
}

sub dbi {
    my $self = shift;

    if (defined $self->{'dbh'}) {
        return $self->{'dbh'};
    }
    else {
        my $dbhost = $self->{'conf'}->{'database'}->{'hostname'};
        my $dbname = $self->{'conf'}->{'database'}->{'database'};
        my $dbuser = $self->{'conf'}->{'database'}->{'username'};
        my $dbpass = $self->{'conf'}->{'database'}->{'password'};

        $self->{'dbh'} = DBI->connect("DBI:mysql:$dbname:$dbhost",
            $dbuser, $dbpass, { PrintError => 1 });

        return $self->{'dbh'};
    }
}

sub connect {
    my $self = shift;
    my $sock = shift;

    if (not defined $sock) {
        if (defined $ENV{'HB_ROOT'}) {
            $sock = $ENV{'HB_ROOT'}."/sock";
        }
        else {
            die "Hackabot control socket location is unknown!";
        }
    }

    my $conn;
    my $addr = sockaddr_un($sock);

    # Not good to die in a module, but whatever
    socket($conn,PF_UNIX,SOCK_STREAM,0) or die "Unable to create a socket!";
    connect($conn, $addr) or die "Unable to Connect to $addr";
    $conn->autoflush(1);

    $self->{'conn'} = $conn;

    my $to = $self->reply_to;
    if ($to) {
        $self->cmd("to $to");
    }
}

sub close {
    my $self = shift;

    if (defined $self->{'conn'}) {
        close $self->{'conn'};
        $self->{'conn'} = undef;
    }

    if (defined $self->{'dbh'}) {
        $self->{'dbh'}->disconnect;
        $self->{'dbh'} = undef;
    }
}

sub cmd {
    my ($self, $send) = @_;

    if (not defined($self->{'conn'})) {
        $self->connect;
    }

    my $conn = $self->{'conn'};

    if (defined $ENV{'HB_NETWORK'}) {
       print $conn "net " . $ENV{'HB_NETWORK'} . "\n";
       my $net_ret = <$conn>;
    }

    print $conn "$send\n";
    my $ret = <$conn>;

    if (not defined $ret) {
        $ret = "error connection lost with no result";
    }

    chomp $ret;
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

sub time {
    return localtime($ENV{'HBEV_TIME'});
}

sub sent_by {
    if (defined $ENV{'HBEV_SENT_BY'}) {
        return $ENV{'HBEV_SENT_BY'};
    }
    else {
        return "";
    }
}

sub sent_to {
    if (defined $ENV{'HBEV_SENT_TO'}) {
        return $ENV{'HBEV_SENT_TO'};
    }
    else {
        return "";
    }
}

sub reply_to {
    if (defined $ENV{'HBEV_REPLY_TO'}) {
        return $ENV{'HBEV_REPLY_TO'};
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

sub names {
    my ($self, $chan) = @_;

    my $names = $self->cmd("names $chan");
    if ($names =~ /^ok\s+(\S.*)/) {
        my @list = split(/\s+/, $1);
        return @list;
    }
    else {
        print STDERR $names;
    }
}

sub counter_add {
    my ($self, $type, $name, $val) = @_;
    my $nick = $self->sent_by;
    my $chan = $self->channel;
    my ($dbh, $sth);

    $val =~ /^(-?\d+)$/ or die;
    die if ($type =~ /^\w$/ or not defined $name or not defined $val);

    $dbh = $self->dbi;
    $sth = $dbh->prepare("INSERT INTO `$type`
        (`name`, `value`, `nick`, `chan`, `date`)
        VALUES (?, ?, ?, ?, FROM_UNIXTIME(?))
        ON DUPLICATE KEY UPDATE
        `value` = `value` + VALUES(`value`), 
        `nick` = VALUES(`nick`),
        `chan` = VALUES(`chan`),
        `date` = VALUES(`date`)");
    $sth->execute($name, $val, $nick, $chan, $ENV{'HBEV_TIME'})
        or die "DB insert failed!";
}

sub counter_get {
    my ($self, $type, $name) = @_;
    my ($dbh, $sth, $val);

    die if ($type =~ /^\w$/ or not defined $name);

    $dbh = $self->dbi;
    $sth = $dbh->prepare("SELECT `value` FROM `$type` WHERE `name` = ?");
    $sth->execute($name) or die "DB select failed!";
    $val = $sth->fetchrow_array;

    return $val;
}

sub counter_list {
    my ($self, $type, $order, $chan) = @_;
    my ($dbh, $sth);

    die if ($type =~ /^\w$/);

    if (not defined $order) {
        $order = "";
    }

    $dbh = $self->dbi;

    my $where = "";
    if (defined $chan) {
        $where = "WHERE 0";
        foreach $_ ($self->names($chan)) {
            $_ = $dbh->quote($_);
            $where .= " OR name = $_";
        }
    }

    $sth = $dbh->prepare("SELECT `name`, `value` FROM `$type` $where
        ORDER BY value $order LIMIT 3");
    $sth->execute or die "DB select failded!";
    return @{$sth->fetchall_arrayref({})};
}

sub quote_get {
    my $self = shift;
    my $type = shift;
    my $search = shift;  # optional
    my ($dbh, $sth);

    $dbh = $self->dbi or die;

    # do some input validation
    if (defined($search)) {
        if ($search !~ /^%|%$/) {
            $search = '%' . $search . '%';
        }
        $search = $dbh->quote($search);
        $search = qq| WHERE `text` LIKE $search |;
    } else {
        $search = "";
    }

    my $sql = qq{SELECT `id`, `text` FROM `$type` $search
        ORDER BY RAND()*`lastused` ASC LIMIT 1};
    $sth = $dbh->prepare($sql);
    $sth->execute or die;
    my @row = $sth->fetchrow_array;
    my $value = $row[1];
    my $id = $row[0];

    # Not sure why I originally used this format instead of just using
    # seconds since epoch, but I'll stick with it for compatibility's sake.
    my $time = localtime->strftime("%y%m%d%H%M");

    $dbh->do("UPDATE `$type` SET lastused = ? WHERE id = ?",
        undef, $time, $id) or die;

    return $value;
}

sub quote_add {
    my ($self, $type, $text, $set_lastused) = @_;
    my $nick = $self->sent_by;
    my $chan = $self->channel;
    my $lastused = "'1'";

    if (defined($set_lastused) and $set_lastused) {
        $lastused = "NOW()";
    }

    my $dbh = $self->dbi or die;

    $dbh->do("INSERT `$type`
        (`text`, `nick`, `chan`, `date`, `lastused`)
        VALUES (?, ?, ?, NOW(), $lastused)",
        undef, $text, $nick, $chan) or die;
}

1;
