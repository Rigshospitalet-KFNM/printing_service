from printing.services import CupsCLIService

cups = CupsCLIService()
print(cups.list_printers())