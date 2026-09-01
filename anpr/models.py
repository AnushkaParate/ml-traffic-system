# This app holds the number-plate localization + EasyOCR pipeline
# (Weeks 2-3 of the roadmap). No DB models needed here -- it reads a
# cropped plate image and returns a matched accounts.models.Vehicle
# (or None if no confident match). Keep OCR scripts here, e.g.:
#   anpr/plate_crop.py   -- locate plate region in a frame
#   anpr/ocr.py          -- run EasyOCR + clean output text
#   anpr/matcher.py      -- fuzzy-match OCR text against Vehicle.plate_number
