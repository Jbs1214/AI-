from ultralytics import SAM
import time
import cv2

# sam_b(빠름), sam_l(정확)
model = SAM("sam_b.pt")

image_path = "261019_5_yolo_advan2\sam.jpg"

start_time = time.time()

results = model(image_path, save= True)

end_time = time.time()

no_label_output = results[0].plot(labels=False, boxes = False)

if_time = end_time - start_time

cv2.imwrite("./output_sam.jpg", no_label_output)
print(f"총 추론 시간 : {if_time:.2f}")
print("추론 완료")

