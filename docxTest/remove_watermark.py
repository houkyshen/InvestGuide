import cv2
import numpy as np
import os
from tqdm import tqdm

# 配置区（按你图里的水印位置，先扩大范围试试）
INPUT_DIR = "images/media"
OUTPUT_DIR = "clean"
DEBUG_DIR = "debug"  # 调试用，看掩码位置
WATERMARK_X, WATERMARK_Y = 800, 10  # 向左、向上扩一点
WATERMARK_W, WATERMARK_H = 450, 100  # 宽高都加大，确保完全盖住水印

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)
exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(exts)]

if not files:
    print("❌ 错误：images 文件夹里没有找到图片文件！")
    exit()

# 只处理第一张图，用于调试
first_img = files[0]
path = os.path.join(INPUT_DIR, first_img)
img = cv2.imread(path)
if img is None:
    print(f"❌ 无法读取图片：{path}")
    exit()

# 生成调试图：用红色框标出掩码区域
debug_img = img.copy()
cv2.rectangle(
    debug_img,
    (WATERMARK_X, WATERMARK_Y),
    (WATERMARK_X + WATERMARK_W, WATERMARK_Y + WATERMARK_H),
    (0, 0, 255),  # 红色
    3
)
cv2.imwrite(os.path.join(DEBUG_DIR, "debug_mask.png"), debug_img)
print(f"✅ 调试图已生成：debug/debug_mask.png，请检查红色框是否完全盖住水印")

# 批量处理
for fname in tqdm(files, desc="去水印中"):
    path = os.path.join(INPUT_DIR, fname)
    img = cv2.imread(path)
    if img is None:
        print(f"⚠️ 跳过无法读取的图片：{fname}")
        continue

    # 防止越界
    h, w = img.shape[:2]
    x_end = min(WATERMARK_X + WATERMARK_W, w)
    y_end = min(WATERMARK_Y + WATERMARK_H, h)
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[WATERMARK_Y:y_end, WATERMARK_X:x_end] = 255

    # 修复（改用更适合大面积修复的算法）
    result = cv2.inpaint(img, mask, 5, cv2.INPAINT_NS)  # 5是修复半径，INPAINT_NS对大面积效果更好

    cv2.imwrite(os.path.join(OUTPUT_DIR, fname), result)

print("✅ 全部处理完成！")