from PIL import Image, ImageEnhance, ImageOps   # Pillow — 이미지 열기·변환·저장 라이브러리
import matplotlib.pyplot as plt                 # matplotlib — 그래프·이미지를 화면에 그려 보여주는 시각화 라이브러리
import cv2

# [1단계] 이미지 불러오기 — PNG·JPG 모두 가능
img = Image.open("original.jpg")


# # [2단계] 회전 — 90도 반시계 방향
img_rotated = img.rotate(90)

# [3단계] 밝기 조절 — 0.5 = 원본의 50%
enhancer = ImageEnhance.Brightness(img)
img_brightness = enhancer.enhance(0.5)

# # [4단계] 좌우 반전 — 거울처럼 뒤집기
img_flip = ImageOps.mirror(img)

# 대비 조절 — 1.5 = 원본의 150%
img_contrast = ImageEnhance.Contrast(img).enhance(1.5)

# 흑백 변환 — 컬러 정보를 제거하고 밝기만 남기기
img_gray = img.convert("L")

# [5단계] 시각화 — 원본·변환 결과를 한 화면에 비교
fig, ax = plt.subplots(2, 3, figsize=(20, 10))

# 원본
ax[0,0].imshow(img)
ax[0,0].axis('off')
ax[0,0].set_title("Original")

# 회전
ax[0,1].imshow(img_rotated)
ax[0,1].axis('off')
ax[0,1].set_title("Rotated 90")

# 밝기
ax[0,2].imshow(img_brightness)
ax[0,2].axis('off')
ax[0,2].set_title("Brightness")

# 좌우 반전
ax[1,0].imshow(img_flip)
ax[1,0].axis('off')
ax[1,0].set_title("Flip")

# 대비
ax[1,1].imshow(img_contrast)
ax[1,1].axis('off')
ax[1,1].set_title("Contrast")

# 흑백
ax[1,2].imshow(img_gray, cmap='gray')
ax[1,2].axis('off')
ax[1,2].set_title("Grayscale")

plt.show()

# [6단계] 저장 — 변환된 이미지 5장 출력
img_rotated.save("./img_rotated.jpg")
img_brightness.save("./img_brightness.jpg")
img_flip.save("./img_flip.jpg")
img_contrast.save("./img_contrast.jpg")
img_gray.save("./img_gray.jpg")

print("이미지 저장이 잘 됐습니다.")