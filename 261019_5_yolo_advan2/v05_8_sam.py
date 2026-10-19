from ultralytics import SAM
import time

# sam_b(빠름), sam_l(정확)
model = SAM("sam_b.pt")

image_path = "261019_5_yolo_advan2\sam.jpg"

start_time = time.time()

model(image_path, save= True)

end_time = time.time()

if_time = end_time - start_time
print(f"총 추론 시간 : {if_time:.2f}")
print("추론 완료")

