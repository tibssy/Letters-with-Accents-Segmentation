import cv2
import numpy as np


def segmentation(img):
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    stats = cv2.connectedComponentsWithStats(thresh, connectivity=8)[2][1:]
    stats = stats[np.argsort(stats[:, 0])]
    stats_mod = np.copy(stats)
    stats_mod[:, 2] = stats[:, 0] + stats[:, 2]
    stats_mod[:, 3] = stats[:, 1] + stats[:, 3]
    avg_h = np.average(stats[:, 3])
    res = stats_mod[stats[:, 3] >= avg_h / 2]
    accents = stats_mod[stats[:, 3] < avg_h / 2]

    for pos in accents:
        diff_min = np.argmin(np.sum(np.abs(res[:, :2] - pos[:2]), axis=1))

        if res[diff_min][1] > pos[1] and res[diff_min][1] - pos[1] < avg_h / 1.5:
            res[diff_min][1] = pos[1]
        if res[diff_min][0] > pos[0] and res[diff_min][0] <= pos[2]:
            res[diff_min][0] = pos[0]
        if res[diff_min][2] < pos[2] and res[diff_min][2] >= pos[0]:
            res[diff_min][2] = pos[2]

    return res[:, :4]


image = cv2.imread('sample.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
segments = segmentation(gray)
print(segments)

for segment in segments:
    x1, y1, x2, y2 = segment[:4]
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

cv2.imshow('image', image)
cv2.waitKey()
