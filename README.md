# printing_service
## Cli_broker
A lightweight Python broker for sending print jobs to the internal `hopper` CUPS server.

## Pycups_broker
A more versitile modern broker for sending print jobs to a cups server.


## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/yourusername/printing-service.git
```
Or clone the repo for local development and install manually:
```bash
git clone https://github.com/yourusername/printing-service.git
cd printing-service
pip install .
```
<br />

### usage

```
from printing_service import CupsCLIService/CupsPyService

cups = CupsCLIService()/CupsPyService()

# List all printers
printers = cups.list_printers()

# Access a specific printer 
printer = printers["william"] #cli_broker
get_printer("William") #pycups_broker

# Check if printer is reachable (enabled and online)
print(printer.is_reachable())

# Print a file
cups.print("william", "/path/to/file.ps", user="tester") #cli_broker
cups.print_file("william", "/path/to/file.ps") #pycups_broker

# Print raw text
cups.print("william", "Hello world", user="tester") #cli_broker
cups.print_text("william", "Hello world", "testFile") #pycups_broker

# Safe print (only sends job if printer is reachable) (cli_broker only)
cups.safe_print(printer, "/path/to/file.ps", user="tester")

# List all jobs
cups.list_jobs()

# List jobs for a specific printer 
cups.list_jobs("william") #cli_broker
get_printer_jobs("william") #pycups_broker
```

Limited documentation for CupsCLIService:
```
CupsCLIService

list_printers() → dict[str, Printer]
Returns all printers, keyed by name.

list_jobs(printer: Optional[str] = None) → list[Job]
Returns print jobs. If printer is given, only jobs for that printer.

print(printer_name: str, path_or_text: str, user: Optional[str] = None)
Creates a print job for the given printer. Accepts either a file path or raw text.

safe_print(printer: Printer, path_or_text: str, user: Optional[str] = None)
Like print(), but checks that the printer is reachable before submitting the job.
```

```
Printer

is_reachable() → bool
Returns True if the printer is enabled and responds to a socket connection.
```
```
Job

Represents a print job (ID, owner, size, status, etc.).
```

## notes
### Cli_broker
- Requires `lq` and `lqstat` to be available in the system (`cups-client` package)
- This is hardcoded to speak to hopper.petnet.rh.dk
### Pycups_broker
- Requires the CUPS library for python (pycups) to function