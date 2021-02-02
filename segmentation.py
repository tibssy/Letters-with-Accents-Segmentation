import cv2
import numpy as np
import fnmatch
import os


def segmentation(img):
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
        if res[diff_min][0] > pos[0] and res[diff_min][0] <= pos[2] + (pos[2] - pos[0]) / 2:
            res[diff_min][0] = pos[0]
        if res[diff_min][2] < pos[2] and res[diff_min][2] >= pos[0] - (pos[2] - pos[0]) / 2:
            res[diff_min][2] = pos[2]

    return res[:, :4]

def save_to_file(segments):
    folder_name = '{}_fonts'.format(filename[:-4])
    os.system('mkdir {}'.format(folder_name))
    for num in range(segments.shape[0]):
        x1, y1, x2, y2 = segments[num][:4]
        roi = gray[y1-1:y2+1, x1-1:x2+1]
        bordered = cv2.copyMakeBorder(roi, border, border, border, border, cv2.BORDER_CONSTANT, value = white)
        cv2.imwrite('{0}/{1}_{2}.png'.format(folder_name, filename[:-4], num), bordered)
    
def draw_rect(segments):
    for segment in segments:
        x1, y1, x2, y2 = segment[:4]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
    

border = 20
white = [255,255,255]
filename = fnmatch.filter(os.listdir('.'), '*.png')[0]


image = cv2.imread(filename)
size_y, size_x = image.shape[:2]
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
segments = segmentation(thresh)
draw_rect(segments)

if size_x > 280:
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, "Press 'S' to Save", (int(size_x / 2) - 140, size_y - 8), font, 1, (255,0,76), 2, cv2.LINE_AA)
    
print("Press 'S' to Save")
    
cv2.imshow('image', image)
k = cv2.waitKey(0)
if k == 27:
    cv2.destroyAllWindows()
elif k == ord('s'):
    save_to_file(segments)
    cv2.destroyAllWindows()
