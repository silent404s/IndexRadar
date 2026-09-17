import csv

def export_to_csv(filepath, data_rows):
    """
    Mengekspor list data_rows ke file CSV dengan format UTF-8 BOM untuk kompatibilitas Excel.
    data_rows format: [[no, domain, status, count, detail], ...]
    """
    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["No", "Domain", "Status", "Jumlah Index", "Keterangan"])
            for row in data_rows:
                writer.writerow(row)
        return True, None
    except Exception as e:
        return False, str(e)
