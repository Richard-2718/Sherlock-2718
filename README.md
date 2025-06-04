# Sherlock-2718

This repository demonstrates how to compute the offset between an image center and a detection bounding box using an ONNX model. The result is sent over a serial port to a connected STM32 board. The logic can also be wrapped into a ROS node for integration with a larger system.

## Scripts

- `src/offset_serial.py` – Runs inference on a single image and sends the resulting offset over a serial port.
- `src/ros_offset_node.py` – ROS node that subscribes to an image topic, computes the offset for each frame and sends it over serial while also publishing the offset.

## Usage

### Stand‑alone
```bash
python3 src/offset_serial.py --model model.onnx --image frame.jpg --port /dev/ttyUSB0
```

### As a ROS node

Launch the node after making sure `rospy` and `cv_bridge` are installed:
```bash
rosrun your_package ros_offset_node.py _model_path:=model.onnx _serial_port:=/dev/ttyUSB0
```
The node listens to the `image` topic and publishes `offset` containing `[dx, dy]`.
