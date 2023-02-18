# journald.conf

Talk through:
- Storage=
- RateLimit...=
- System...=/Runtime...=
- Forward...=
- MaxLevel...=





# writing to the journal

## run service - stdout and stderr go to the journal

`systemctl start journal_hello`

## using systemd-cat

`systemd-cat echo "Hello from systemd cat!"`

## programmatically with sd-journal library

`gcc -l systemd journal_print.c`
./a.out





# viewing/traversing journal logs

## journal logs sorted oldest to newest

`journalctl`

## journal logs sorted newest to oldest

`journalctl -r`

## list boots

journalctl --list-boots

## logs from current boot

journalctl -b

## show kernel messages - talk about how all logs are interleaved in the journal

journalctl --dmesg

## grep the journal

`journalctl -g Hello*`

## show logs from the unit

`journalctl -u journal_hello.service`

## view metadata fields

`journalctl --output verbose`
`journalctl -u journal_hello.service --output verbose`

## view logs from PID 1

`journalctl _PID=1`
`journalctl -u journal_hello.service _PID=1`

## time range

`journalctl --since -30min`
`journalctl -u journal_hello.service --since -30min`
`journalctl -u journal_hello.service --since -30min _PID=1`