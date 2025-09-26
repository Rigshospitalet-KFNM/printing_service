import re
import subprocess
import tempfile
from typing import Optional, Union
from printing.objects import Printer, Job
from pathlib import Path


class CupsCLIService:
    def __init__(self, host="hopper.petnet.rh.dk:631/version=1.1"):
        self.host = host
    
    def list_printers(self):
        raw_text = self._run_lpstat()
        return self._parse_printers(raw_text)
    

    def print(
        self,
        printer_name: str,
        content: Union[str, Path],
        number: int = 1,
        user: Optional[str] = None
    ):
        """
        Print either a string (raw text) or a file (Path or string path).
        """
        try:
            if isinstance(content, Path) or (isinstance(content, str) and Path(content).exists()):
                # It's a file path
                output = self._print_file(printer_name, str(content), number, user)
            else:
                # Treat as raw text
                output = self._print_text(printer_name, str(content), number, user)
            return {"success": True, "message": output}
        except RuntimeError as e:
            return {"success": False, "message": str(e)}


    #subprocesses-----------

    #printing
    def _print_file(self, printer_name: str, file_path: str, number: int = 1, user: Optional[str] = None):
        cmd = ["lp", "-h", self.host, "-d", printer_name, "-n", str(number)]
        if user:
            cmd.extend(["-U", user])
        cmd.append(file_path)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Print failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def _print_text(self, printer_name: str, text: str, number: int = 1, user: Optional[str] = None):
        # Write text to a temporary file and print
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write(text)
            tmp.flush()
            return self._print_file(printer_name, tmp.name, number, user)


    #query
    def _run_lpstat(self):
        result = subprocess.run(
            ["lpstat", "-h", self.host, "-l", "-v", "-p"],
            capture_output=True
        )
    
        return result.stdout.decode("latin-1") #Should be UTF-8 but hopper is too old


    #parsing
    def _parse_printers(self, raw_text: str) -> dict[str, Printer]:
        printers: dict[str, Printer] = {}
        device_map: dict[str, str] = {}

        pattern_device = re.compile(
            r"device for (\S+):\s+(\S+)"
        )       

        pattern_enabled = re.compile(
            r"(?:printer )?(\S+)\s+(?:is\s+(\w+)|now printing (\S+))\. +enabled since (.+)"        
        )
        pattern_disabled = re.compile(
            r"(?:printer )?(\S+) disabled since (.+?) -$"
        )

        current_block: list[str] = []

        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # First check for device lines
            match_device = pattern_device.match(line)
            if match_device:
                name, uri = match_device.groups()
                device_map[name] = uri
                continue

            # Check if line starts a new printer
            if pattern_enabled.match(line) or pattern_disabled.match(line):
                if current_block:
                    printer = self._parse_block(current_block, pattern_enabled, pattern_disabled)
                    if printer:
                        printers[printer.name] = printer
                        # attach device_uri if known
                        printer.device_uri = device_map.get(printer.name)
                current_block = [line]
            else:
                current_block.append(line)

        # Process the last block
        if current_block:
            printer = self._parse_block(current_block, pattern_enabled, pattern_disabled)
            if printer:
                printers[printer.name] = printer
                printer.device_uri = device_map.get(printer.name)

        return printers

    # parser helper function
    def _parse_block(self, block_lines: list[str], pattern_enabled, pattern_disabled) -> Printer | None:
        header = block_lines[0]
        details = block_lines[1:]

        # parse header
        match_enabled = pattern_enabled.match(header)
        match_disabled = pattern_disabled.match(header)

        printer: Printer | None = None

        if match_enabled:
            name = match_enabled.group(1)
            status_word = match_enabled.group(2)
            job_id = match_enabled.group(3)
            since = match_enabled.group(4)

            if job_id:
                status = "printing"
                current_job = job_id
            else:
                status = status_word
                current_job = None

            printer = Printer(
                name=name,
                status=status,
                enabled=True,
                since=since,
                current_job=current_job,
            )
        elif match_disabled:
            name, since = match_disabled.groups()
            printer = Printer(
                name=name,
                status="disabled",
                enabled=False,
                since=since,
                description=None,
                location=None,
                error=None,
            )

        if printer is None:
            return None  # skip invalid blocks

        # parse details
        for line in details:
            line = line.strip()
            if line.startswith("Description:"):
                printer.description = line.split(":", 1)[1].strip()
            elif line.startswith("Location:"):
                printer.location = line.split(":", 1)[1].strip()
            elif "error" in line.lower() or line.startswith("/"):
                printer.error = line

        return printer
