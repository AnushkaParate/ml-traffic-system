# This app holds the YOLOv8 inference code for helmet, triple-riding, and
# ambulance detection (Weeks 2-4 of the roadmap). It doesn't need its own
# DB models -- it writes results into challan.models.Violation once a
# violation is confirmed. Keep detection scripts here, e.g.:
#   detection/inference.py   -- load YOLO model, run on a video frame
#   detection/helmet.py      -- helmet-specific post-processing
#   detection/triple_riding.py
#   detection/ambulance.py
