#!/usr/bin/env perl
use warnings;
use strict;
use open IO => ":locale";

my %counts;

while (<>) {
    s{\R\z}{};
    my @chars = split('', $_);
    foreach my $char (@chars) {
        $counts{ord($char)} += 1;
    }
}

foreach my $codepoint (sort { $a <=> $b } keys %counts) {
    printf("%d\n", $codepoint);
}
