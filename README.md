# netpython

A Python implementation of core netcat functionality — TCP listen/connect,
an interactive remote command shell, remote command execution, and file
upload — built as a hands-on exercise in socket programming (based on the
"BHP Net Tool" exercise from *Black Hat Python*).

⚠️ **For educational and authorized-testing use only.** This tool can
execute shell commands and transfer files over a network connection.
Only run it against systems you own or have explicit permission to test.

## What it does

- **Listen mode** — binds and listens on a given host/port for incoming
  connections, threaded to handle multiple clients
- **Connect mode** — connects out to a remote host/port, sends stdin,
  and prints responses
- **Command shell (`-c`)** — spins up an interactive remote shell prompt
  (`BHP: #>`) that executes whatever commands are sent to it
- **Execute (`-e`)** — runs a single specified command on connection and
  returns the output
- **Upload (`-u`)** — receives a file over the socket and writes it to disk

## Requirements

- Python 3
- No external dependencies — standard library only (`socket`, `argparse`,
  `subprocess`, `threading`)

## Usage

```bash
# Start a listener with an interactive command shell
python netcat.py -t 0.0.0.0 -p 5555 -l -c

# Start a listener that executes a specific command on connect
python netcat.py -t 0.0.0.0 -p 5555 -l -e "whoami"

# Start a listener that saves an uploaded file
python netcat.py -t 0.0.0.0 -p 5555 -l -u received_file.txt

# Connect to a listener as a client
python netcat.py -t 192.168.1.108 -p 5555

# Pipe text to a remote listener
echo "hello" | python netcat.py -t 192.168.1.108 -p 5555
```

## Why I built it

A socket-programming exercise to understand how tools like netcat work
under the hood — TCP listeners, threaded connection handling, and piping
data between a local shell and a remote socket.

## License

MIT (or your preference)
