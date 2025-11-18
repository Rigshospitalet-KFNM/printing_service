import cups #Dependency
from pathlib import Path
from typing import Optional, Union
from printing_service.objects import Printer, Job 

'''
More mordern broker using pycups -> dependency
Is faster and more stable than cli_broker, use when able
'''

class CupsPyService:
    def __init__(self, host: str = "localhost", port: int = 631, user: Optional[str] = None):
        self.host = host
        self.port = port
        self.user = user

        # Connect to a remote or local CUPS server
        if host == "localhost":
            self.conn = cups.Connection()
        else:
            self.conn = cups.Connection(f"http://{host}:{port}")

    # -----------------------------
    # Printers
    # -----------------------------
    def list_printers(self) -> dict[str, Printer]:
        """Return a dictionary of printers from CUPS."""
        printers_raw = self.conn.getPrinters()
        printers: dict[str, Printer] = {}

        for name, info in printers_raw.items():
            printers[name] = Printer(
                name=name,
                description=info.get("printer-info"),
                location=info.get("printer-location"),
                status="idle" if not info.get("printer-state-message") else info.get("printer-state-message"),
                enabled=info.get("printer-is-shared", True),
                device_uri=info.get("device-uri"),
                since=None,
                current_job=None,
            )

        return printers

    def get_printer(self, name: str) -> Optional[Printer]:
        """Fetch a single printer by name."""
        printers = self.list_printers()
        return printers.get(name)

    # -----------------------------
    # Printing
    # -----------------------------
    def print_file(self, printer_name: str, file_path: Union[str, Path], title: Optional[str] = None, copies: int = 1):
        """Submit a print job using a file path."""
        path = str(file_path)
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")

        job_id = self.conn.printFile(
            printer_name,
            path,
            title or Path(path).name,
            {"copies": str(copies)}
        )
        return {"success": True, "job_id": job_id}

    def print_text(self, printer_name: str, text: str, title: str = "Raw Text Job", copies: int = 1):
        """Print raw text by writing it to a temporary file first."""
        import tempfile

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write(text)
            tmp.flush()
            return self.print_file(printer_name, tmp.name, title, copies)

    # -----------------------------
    # Jobs
    # -----------------------------
    def list_jobs(self, which: str = "all") -> list[Job]:
        """
        List jobs.
        which: 'completed', 'not-completed', or 'all'
        """
        jobs_raw = self.conn.getJobs(which_jobs=which)
        jobs: list[Job] = []

        for job_id, attrs in jobs_raw.items():
            jobs.append(Job(
                id=job_id,
                name=attrs.get("job-name"), # type: ignore
                user=attrs.get("job-originating-user-name"),
                printer=attrs.get("job-printer-name"),
                status=attrs.get("job-state"),
                size=attrs.get("job-k-octets"),
                pages=attrs.get("job-media-sheets-completed"),
            ))

        return jobs
    
    def get_printer_jobs(self, printer_name: str, which: str = "all") -> list[Job]:
        jobs_raw = self.conn.getJobs(which_jobs=which, my_jobs=False)
        jobs = []
    
        for job_id, attrs in jobs_raw.items():
            if attrs.get("job-printer-name") != printer_name:
                continue
            
            jobs.append(Job(
                id=job_id,
                name=attrs.get("job-name"), # type: ignore
                user=attrs.get("job-originating-user-name"),
                printer=attrs.get("job-printer-name"),
                status=attrs.get("job-state"),
                size=attrs.get("job-k-octets"),
                pages=attrs.get("job-media-sheets-completed"),
            ))
        return jobs

    def cancel_job(self, job_id: int):
        """Cancel a specific job."""
        self.conn.cancelJob(job_id)
        return {"success": True, "message": f"Job {job_id} cancelled"}

    # -----------------------------
    # Admin / Maintenance
    # -----------------------------
    def enable_printer(self, printer_name: str):
        self.conn.enablePrinter(printer_name)
        return {"success": True, "message": f"Printer {printer_name} enabled"}

    def disable_printer(self, printer_name: str):
        self.conn.disablePrinter(printer_name)
        return {"success": True, "message": f"Printer {printer_name} disabled"}

    def restart_printer(self, printer_name: str):
        self.conn.restartPrinter(printer_name)
        return {"success": True, "message": f"Printer {printer_name} restarted"}