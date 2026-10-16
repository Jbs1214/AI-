from ultralytics import YOLO
import cv2

model = YOLO("yolo11x.pt")

results = model("261014_2_yolo_basic/safari.jpg")

results_image = results[0].plot()

output_image_path = "./images/yolo_img/output2.jpg"

save_result_img = cv2.imwrite(output_image_path,results_image)

