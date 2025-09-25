import re
import subprocess
from printing.objects import Printer, Job


class CupsCLIService:
    def list_printers(self):
        raw_text = self._run_lpstat()
        return self._parse_printers(raw_text)


    #subprocesses
    def _run_lpstat(self):
        result = subprocess.run(
            ["lpstat", "-h", "hopper.petnet.rh.dk:631/version=1.1", "-l", "-p"],
            capture_output=True
        )
    
        return result.stdout.decode("latin-1") #Should be UTF-8 but hopper is too old


    #parsing
    def _parse_printers(self, raw_text: str) -> dict[str, Printer]:
        printers: dict[str, Printer] = {}

        pattern_enabled = re.compile(
            r"(?:printer )?(\S+) is (\w+)(?: (\d+) job)?\. +enabled since (.+)"
        )
        pattern_disabled = re.compile(
            r"(?:printer )?(\S+) disabled since (.+?) -$"
        )

        current_block: list[str] = []

        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Check if line starts a new printer
            if pattern_enabled.match(line) or pattern_disabled.match(line):
                if current_block:
                    printer = self._parse_block(current_block, pattern_enabled, pattern_disabled)
                    if printer:
                        printers[printer.name] = printer
                current_block = [line]
            else:
                current_block.append(line)

        # Process the last block
        if current_block:
            printer = self._parse_block(current_block, pattern_enabled, pattern_disabled)
            if printer:
                printers[printer.name] = printer

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
            name, status, jobs, since = match_enabled.groups()
            jobs = int(jobs) if jobs else 0
            printer = Printer(
                name=name,
                status=status,
                enabled=True,
                jobs=jobs,
                since=since,
                description=None,
                location=None,
                error=None,
            )
        elif match_disabled:
            name, since = match_disabled.groups()
            printer = Printer(
                name=name,
                status="disabled",
                enabled=False,
                jobs=0,
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
