#!/usr/bin/env python3
"""Compute bounding box offset and send via serial.

This script loads an ONNX model, runs inference on an image,
computes the offset between the image center and the bounding box
center, and sends the offset over a serial connection.
"""

from dataclasses import dataclass
import cv2
import numpy as np
import onnxruntime as ort
import serial

@dataclass
class OffsetResult:
    dx: float
    dy: float

class OffsetCalculator:
    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        _, _, self.in_h, self.in_w = self.session.get_inputs()[0].shape

    def compute(self, image: np.ndarray) -> OffsetResult:
        h, w = image.shape[:2]
        resized = cv2.resize(image, (self.in_w, self.in_h))
        input_data = resized.transpose(2, 0, 1).astype(np.float32)[None, :]
        outputs = self.session.run(None, {self.input_name: input_data})
        bbox = outputs[0][0]  # [x1, y1, x2, y2]
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        dx = float(cx - w / 2.0)
        dy = float(cy - h / 2.0)
        return OffsetResult(dx=dx, dy=dy)

def send_offset(port: str, offset: OffsetResult, baudrate: int = 115200):
    """Send offset as 'dx,dy\n' via serial."""
    with serial.Serial(port=port, baudrate=baudrate, timeout=1) as ser:
        msg = f"{offset.dx:.2f},{offset.dy:.2f}\n"
        ser.write(msg.encode("utf-8"))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run ONNX model and send offset over serial")
    parser.add_argument("--model", required=True, help="Path to ONNX model")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--port", required=True, help="Serial port device")
    args = parser.parse_args()

    img = cv2.imread(args.image)
    if img is None:
        raise FileNotFoundError(args.image)

    calc = OffsetCalculator(args.model)
    offset = calc.compute(img)
    send_offset(args.port, offset)
    print(f"Sent offset: dx={offset.dx:.2f}, dy={offset.dy:.2f}")


if __name__ == "__main__":
    main()
