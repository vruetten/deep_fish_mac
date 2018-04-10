#!/usr/bin/python3
import numpy as np
import cv2


class MyRealTimeTracker(object):
    def __init__(self, args):

        self.args = args
        self.pVal = args['pVal']
        self.pVal_mx = args['pVal_mx']
        self.fishNum = args['fishNum']
        self.area_mn = args['area_mn']
        self.keypoints = self.args['keypoints']
        self.pre_frames = self.args['pre_frames']


    def blur_frame(self, frame):
        try:
            self.blurWin = (3,3)
            self.blur = cv2.GaussianBlur(frame, self.blurWin, 1)
        except:
            print('no frame found...')
        return self.blur


    def delta_frame(self,mvAvgFrame, gray):
        '''mvAvgFrame, gray as type uint8 '''

        self.frameDelta = np.abs(mvAvgFrame.astype('float32')-gray.astype('float32'))
        self.fD = np.copy(self.frameDelta).astype('uint8')
        return self.fD

    def mask_frame(self,fD, pVal, pVal_mx):
        '''mask frame between values '''

        self.mask = (self.fD>self.pVal)*(self.fD<self.pVal_mx)
        self.masked = np.zeros_like(self.fD)
        self.masked[self.mask] = self.fD[self.mask]

        #self.mask = (fD.copy()>pVal)*(fD.copy()<pVal_mx)*1
        #self.masked = np.zeros_like(fD.copy())
        #self.masked[self.mask] = fD[self.mask].copy()
        return self.mask, self.masked


    def get_frame_contours(self, image2detect, image2print):
        _, cnts, _ = cv2.findContours(image = image2detect, mode = cv2.RETR_EXTERNAL,\
                                      method = cv2.CHAIN_APPROX_SIMPLE)

        self.fD_ = np.repeat(image2print[:,:,None], repeats = 3,axis = 2)

        x = np.array([])
        y = np.array([])
        cX = np.array([])
        cY = np.array([])
        h = np.array([])
        w = np.array([])
        C = []
        a = np.array([])

        for c in cnts[0:5]:
            a_ = cv2.contourArea(c)
            # if the contour is too small, ignore it

            if a_ > self.area_mn:
                a = np.concatenate([a,np.array([a_])])

                M = cv2.moments(c)
                if M["m00"]<1e-9:
                    M["m00"] = 1e10

                cX_ = int(M["m10"] / M["m00"])
                cY_ = int(M["m01"] / M["m00"])

                cX = np.concatenate([cX,np.array([cX_])])
                cY = np.concatenate([cY,np.array([cY_])])

                C.append(c)
                (x_, y_, w_, h_) = cv2.boundingRect(c)
                x = np.concatenate([x,np.array([x_])])
                y = np.concatenate([y,np.array([y_])])
                h = np.concatenate([h,np.array([h_])])
                w = np.concatenate([w,np.array([w_])])


        ## get indices of largest areas
        if len(a)==0:
            self.max_a = -1
        else:
            self.max_a = np.max(a)
        locs = np.argsort(-a[:self.fishNum])
        x = x[locs].astype('int')
        y = y[locs].astype('int')
        cX = cX[locs].astype('int')
        cY = cY[locs].astype('int')
        h = h[locs].astype('int')
        w = w[locs].astype('int')
        a = a[locs].astype('int')
        C = np.array(C)
        C = C[locs]

        cXX =cX.reshape([1,-1])
        cYY =cY.reshape([1,-1])
        xx =x.reshape([1,-1])
        yy =y.reshape([1,-1])
        hh =h.reshape([1,-1])
        ww =w.reshape([1,-1])


        keylen = len(self.keypoints)
        self.keypoints[keylen  + 1] = np.concatenate([cXX, cYY, xx,yy,hh,ww], axis = 0).T
        keylen = len(self.keypoints)

        for i in range(locs.shape[0]):
            self.fD_ = cv2.circle(self.fD_, (cX[i], cY[i]), radius=2, color=(0, 255, 0), thickness=3)
            self.fD_ = cv2.drawContours(self.fD_, C[i], -1, (255,0,255), 5)

        if keylen>25:
            for buf in range(self.pre_frames):
                locs_ = self.keypoints[keylen-buf-1]
                for i in range(locs_.shape[0]):
                    self.fD_ = cv2.circle(self.fD_, (locs_[i,0], locs_[i,1]), radius=1, color=(255, 0, 255), thickness=1)
        self.num_fish_detected = locs.shape[0]

        return self.fD_, self.keypoints, self.num_fish_detected, self.max_a


 #   def write_frame(self):
 #       self.fD_ = cv2.putText(self.fD_, "# fish detected: {}".format(self.text), (10, 300),
 #           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
 #
 #       self.fD_ = cv2.putText(self.fD_, "# frame: {}".format(self.ite), (10, 150),
 #           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
 #
 #       self.fD_ = cv2.putText(self.fD_, "max area: {}".format(self.max_a), (10, 200),
 #           cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
