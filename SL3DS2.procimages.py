import numpy as np
import cv2
import os
import glob
import pickle

"""
def visualizeImages():
  window_name = "test"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 
    cv2.WINDOW_AUTOSIZE)
  cv2.resizeWindow(window_name, 1920, 1048)
  #visualize(window_name, img1, "img1")
  #visualize(window_name, img2, "img2")
  #visualize(window_name, thr1, "thr1")
  #visualize(window_name, thr2, "thr2")
  #visualize(window_name, thresholdImg, "threshold")
  #visualize(window_name, afterImg, "afterThreshold")
  #visualize(window_name, finalImg, "binary")

def visualize(window_name, img_name, img_title):
  base_path = "C:\\Users\\Pedro\\Google Drive\\CMoA_Plaster\\SL - Python Implementation\\HHSL3DScanner\\"
  cv2.imshow(window_name, img_name) #this will show everything in 0 or 1
  cv2.waitKey(10000)
  print("\n\n\n\n\n{} = ".format(img_title))
  row = [img_name[len(img_name)//2][i] for i in range(len(img_name[0]))]
  print (row)
  with open('{}{}.p'.format(base_path, img_title), 'wb') as f: pickle.dump(row, f, protocol = 2)
"""


def imgdesig(img1, img2):
    """
    Determine whether a pixel p is lit or not (1 or 0) in the images.
    Getting dark and light pattern
    """
    old_settings = np.seterr(all='ignore')  # set to ignore float pt errors
    img1 = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)  # convert images to grayscale
    img2 = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)

    # converting the values below 100 (from black to gray) to black
    # originally, the threshold was 10
    ret1, thr1 = cv2.threshold(img1, 10, 255, cv2.THRESH_TOZERO)
    ret2, thr2 = cv2.threshold(img2, 10, 255, cv2.THRESH_TOZERO)

    # divide image 1 by a threshold (the average of image 1 and 2)
    thresholdImg = (((thr1 // 2) + (thr2 // 2)))

    afterImg = (np.divide(thr1, thresholdImg))
    # in numpy versions 1.11.1+ division by 0 results in NaN... trick to solve it:
    afterImg = np.nan_to_num(afterImg)

    finalImg = (np.divide(afterImg, afterImg))
    # in numpy versions 1.11.1+ division by 0 results in NaN... trick to solve it:
    finalImg = np.nan_to_num(finalImg)

    # visualizeImages() #visualize images during the process

    return finalImg


def processingCamera(horzlino, vertlino, img_names):
    # 2 LAYERS TO STORE FINAL VALUES
    camcode = np.zeros((vertlino, horzlino, 2), dtype=np.int16)

    # HORIZONTAL
    grayimg = np.zeros((vertlino, horzlino), dtype=np.int16)
    for ii in range(3, 22, 2):  # 3,22,2
        """
        Horizontal gray code
        ii = 3, 5, 7, 9, 11, 13, 15, 17, 19, 21
        xx = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    
        select an column gray code image and its inverted versions
        (filename1, filename2) = (CAM003, CAM002), (CAM005, CAM004), 
          (CAM007, CAM006) ... (CAM0021, CAM0020)
        """
        xx = (ii - 3) // 2
        filename1, filename2 = img_names[ii], img_names[ii - 1]
        ff = imgdesig(filename1, filename2)
        # print ('processing %s...' % filename1, (2**xx))
        grayimg = grayimg + (2 ** xx) * ff  # converting graycode to decimal

    imgbin3 = np.zeros((vertlino, horzlino, 3), dtype=np.uint8)
    # TRAVERSING THE BASE OF THE MATRIX IMGBIN3
    for ii in range(0, horzlino):
        for jj in range(0, vertlino):
            # using the first layer of camcode to store horizontal values
            camcode[jj][ii][0] = grayimg[jj][ii]
            # doing some crazy operations to display a 3 layer 8-bit matrix as image
            imgbin3[jj][ii][1] = grayimg[jj][ii] % 256  # ????
            imgbin3[jj][ii][2] = 40 * grayimg[jj][ii] // 256  # ????
            imgbin3[jj][ii][0] = 4  # ????

    img1 = (grayimg % 255)  # is this line uselesss?????
    cv2.imshow("PWindow1", imgbin3)  # displaying result for horizontal
    cv2.waitKey(3000)

    # VERTICAL
    # start with image corresponding to the white projection
    img1 = cv2.imread(img_names[0], cv2.IMREAD_GRAYSCALE)
    grayimg = (img1 * 0) + 1023  # matrix full of 1023s?
    grayimg = grayimg * 0  # matrix full of 0s ... why all this code jugglery???

    for ii in range(23, 42, 2):  # 23,42,2

        # Vertical gray code
        # ii = 23, 25, 27, 29, 31, 33, 35, 37, 39, 41
        # xx = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        # select an column gray code image and its inverted versions
        # (filename1, filename2) = (CAM023, CAM022), (CAM025, CAM024),
        #  (CAM027, CAM026) ... (CAM0041, CAM0040)

        xx = (ii - 22) // 2
        filename1, filename2 = img_names[ii], img_names[ii - 1]
        ff = imgdesig(filename1, filename2)
        # print ('processing %s...' % filename1, (2**xx))
        grayimg = grayimg + (2 ** xx) * ff  # converting graycode to decimal

    for ii in range(0, horzlino):
        for jj in range(0, vertlino):
            # using the first layer of camcode to store horizontal values
            camcode[jj][ii][1] = grayimg[jj][ii]
            # doing some crazy update operations on the imgbin3 8-bit matrix
            imgbin3[jj][ii][0] = (imgbin3[jj][ii][0] + grayimg[jj][ii] % 256) % 256
            imgbin3[jj][ii][2] = 40 * (imgbin3[jj][ii][2] + grayimg[jj][ii] % 256) // 80
            imgbin3[jj][ii][1] = 4

    img1 = (grayimg % 255)  # is this line useless again?
    cv2.imshow("PWindow2", imgbin3)
    cv2.waitKey(3000)
    return camcode


# STEP 0: setting variables
print("Start")
base_path = "F:\\COMAPJ\\"
horzlino = 1280  # 1920 #1280
vertlino = 720  # 1080 #768
n_cameras = 2

temp_path_left = base_path + "CAML\\"
img_names_left = glob.glob(temp_path_left + "*.png")
# call for processing the cameras
camcode = processingCamera(horzlino, vertlino, img_names_left)
np.save(temp_path_left + "2_coloccod", camcode)
cv2.waitKey(200)

temp_path_right = base_path + "CAMR\\"
img_names_right = glob.glob(temp_path_right + "*.png")
# call for processing the cameras
camcode = processingCamera(horzlino, vertlino, img_names_right)
np.save(temp_path_right + "2_coloccod", camcode)
cv2.waitKey(200)

cv2.destroyAllWindows()
print('Procimg Done!')