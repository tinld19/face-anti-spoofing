"""Predict video stream spoofing với khả năng tái sử dụng cho GUI."""

import argparse
import time
from dataclasses import dataclass

import cv2
import numpy as np

from src.FaceAntiSpoofing import AntiSpoof
from src.face_detector import YOLOv5


COLOR_REAL = (0, 255, 0)
COLOR_FAKE = (0, 0, 255)
COLOR_UNKNOWN = (127, 127, 127)


def increased_crop(img: np.ndarray, bbox: tuple, bbox_inc: float = 1.5) -> np.ndarray:
    """Cắt khuôn mặt và tăng vùng bao để chống miss alignment."""
    real_h, real_w = img.shape[:2]

    x, y, w, h = bbox
    w, h = w - x, h - y
    l = max(w, h)

    xc, yc = x + w / 2, y + h / 2
    x, y = int(xc - l * bbox_inc / 2), int(yc - l * bbox_inc / 2)
    x1 = 0 if x < 0 else x
    y1 = 0 if y < 0 else y
    x2 = real_w if x + l * bbox_inc > real_w else x + int(l * bbox_inc)
    y2 = real_h if y + l * bbox_inc > real_h else y + int(l * bbox_inc)

    img = img[y1:y2, x1:x2, :]
    img = cv2.copyMakeBorder(
        img,
        y1 - y,
        int(l * bbox_inc - y2 + y),
        x1 - x,
        int(l * bbox_inc) - x2 + x,
        cv2.BORDER_CONSTANT,
        value=[0, 0, 0],
    )
    return img


@dataclass
class PredictionResult:
    bbox: tuple | None
    label: int | None
    score: float | None
    elapsed_ms: float
    face_crop_bgr: np.ndarray | None


class Predictor:
    """Đóng gói suy luận để dùng lại cho CLI và GUI (DRY)."""

    def __init__(
        self,
        model_path: str = "saved_models/AntiSpoofing_bin_1.5_128.onnx",
        detector_path: str = "saved_models/yolov5s-face.onnx",
        threshold: float = 0.5,
        bbox_inc: float = 1.5,
    ):
        self.threshold = threshold
        self.bbox_inc = bbox_inc
        self.face_detector = YOLOv5(detector_path)
        self.anti_spoof = AntiSpoof(model_path)

    def predict(self, frame_bgr: np.ndarray) -> PredictionResult:
        start = time.time()
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        det = self.face_detector([rgb])[0]
        if det is None or det.shape[0] == 0:
            return PredictionResult(None, None, None, (time.time() - start) * 1000, None)

        bbox = det.flatten()[:4].astype(int)
        crop_rgb = increased_crop(rgb, bbox, bbox_inc=self.bbox_inc)
        pred = self.anti_spoof([crop_rgb])[0]
        score = float(pred[0][0])
        label = int(np.argmax(pred))
        elapsed_ms = (time.time() - start) * 1000
        crop_bgr = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2BGR)
        return PredictionResult(tuple(bbox), label, score, elapsed_ms, crop_bgr)

    def annotate(self, frame_bgr: np.ndarray, result: PredictionResult) -> np.ndarray:
        if result.bbox is None:
            return frame_bgr

        (x1, y1, x2, y2) = result.bbox
        if result.label == 0:
            if result.score is not None and result.score > self.threshold:
                res_text = f"REAL {result.score:.2f}"
                color = COLOR_REAL
            else:
                res_text = "unknown"
                color = COLOR_UNKNOWN
        else:
            res_text = f"FAKE {result.score:.2f}"
            color = COLOR_FAKE

        rec_width = max(1, int(frame_bgr.shape[1] / 240))
        txt_offset = int(frame_bgr.shape[0] / 50)
        txt_width = max(1, int(frame_bgr.shape[1] / 480))
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, rec_width)
        cv2.putText(
            frame_bgr,
            res_text,
            (x1, y1 - txt_offset),
            cv2.FONT_HERSHEY_COMPLEX,
            max((x2 - x1) / 250, 0.5),
            color,
            txt_width,
        )
        return frame_bgr

if __name__ == "__main__":
    # parsing arguments
    def check_zero_to_one(value):
        fvalue = float(value)
        if fvalue <= 0 or fvalue >= 1:
            raise argparse.ArgumentTypeError("%s is an invalid value" % value)
        return fvalue
    
    p = argparse.ArgumentParser(
        description="Spoofing attack detection on videostream")
    p.add_argument("--input", "-i", type=str, default=None, 
                   help="Path to video for predictions")
    p.add_argument("--output", "-o", type=str, default=None,
                   help="Path to save processed video")
    p.add_argument("--model_path", "-m", type=str, 
                   default="saved_models/AntiSpoofing_bin_1.5_128.onnx", 
                   help="Path to ONNX model")
    p.add_argument("--threshold", "-t", type=check_zero_to_one, default=0.5, 
                   help="real face probability threshold above which the prediction is considered true")
    args = p.parse_args()

    predictor = Predictor(model_path=args.model_path, threshold=args.threshold)

    # Create a video capture object
    if args.input:  # file
        vid_capture = cv2.VideoCapture(args.input)
    else:           # webcam
        vid_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    frame_width = int(vid_capture.get(3))
    frame_height = int(vid_capture.get(4))
    frame_size = (frame_width, frame_height)
    print('Frame size  :', frame_size)

    if not vid_capture.isOpened():
        print("Error opening a video stream")
    # Reading fps and frame rate
    else:
        fps = vid_capture.get(5)    # Get information about frame rate
        print('Frame rate  : ', fps, 'FPS')
        if fps == 0:
            fps = 24
        # frame_count = vid_capture.get(7)    # Get the number of frames
        # print('Frames count: ', frame_count) 
    
    # videowriter
    output = None
    if args.output:
        output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), fps, frame_size)
    print("Video is processed. Press 'Q' or 'Esc' to quit")
    
    # process frames
    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            result = predictor.predict(frame)
            frame = predictor.annotate(frame, result)

            if args.output:
                output.write(frame)
            
            # if video captured from webcam
            if not args.input:
                cv2.imshow('Face AntiSpoofing', frame)
                key = cv2.waitKey(20)
                if (key == ord('q')) or key == 27:
                    break
        else:
            print("Streaming is Off")
            break

    # Release the video capture and writer objects
    vid_capture.release()
    if output is not None:
        output.release()
    cv2.destroyAllWindows()