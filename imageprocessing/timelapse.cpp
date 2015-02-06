/*
Given numCameras, take a snapshot from each and make a single composite image.
Due to issues with blocking, we write the individual images to disk 
and then read it back from disk to make the final image.
*/
#include <cv.h>
#include "highgui.h"
/*
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
*/
#include <unistd.h>
#include <iostream>
#include <stdio.h>
#include <cstdlib>
using namespace std;
using namespace cv;
 
//http://stackoverflow.com/questions/18121230/how-to-display-one-image-and-one-video-in-one-window-using-opencv
void cvShowManyImages(char* title, int nArgs, ...) {
 
    // img - Used for getting the arguments 
    IplImage *img;
 
    // DispImage - the image in which input images are to be copied
    IplImage *DispImage;
 
    int size;
    int i;
    int m, n;
    int x, y;
 
    // w - Maximum number of images in a row 
    // h - Maximum number of images in a column 
    int w, h;
 
    // scale - How much we have to resize the image
    float scale;
    int max;
 
    // If the number of arguments is lesser than 0 or greater than 12
    // return without displaying 
    if(nArgs <= 0) {
        printf("Number of arguments too small....\n");
        return;
    }
    else if(nArgs > 12) {
        printf("Number of arguments too large....\n");
        return;
    }
    // Determine the size of the image, 
    // and the number of rows/cols 
    // from number of arguments 
    else if (nArgs == 1) {
        w = h = 1;
        size = 300;
    }
    else if (nArgs == 2) {
        w = 2; h = 1;
        size = 300;
    }
    else if (nArgs == 3 || nArgs == 4) {
        w = 2; h = 2;
        size = 300;
    }
    else if (nArgs == 5 || nArgs == 6) {
        w = 3; h = 2;
        size = 200;
    }
    else if (nArgs == 7 || nArgs == 8) {
        w = 4; h = 2;
        size = 200;
    }
    else {
        w = 4; h = 3;
        size = 150;
    }
 
    // Create a new 3 channel image
    DispImage = cvCreateImage( cvSize(100 + size*w, 60 + size*h), 8, 3 );
    cvZero(DispImage);
    // Used to get the arguments passed
    va_list args;
    va_start(args, nArgs);
    // Loop for nArgs number of arguments
    for (i = 0, m = 20, n = 20; i < nArgs; i++, m += (20 + size)) {
 
        // Get the Pointer to the IplImage
        img = va_arg(args, IplImage*);
 
        // Check whether it is NULL or not
        // If it is NULL, release the image, and return
        if(img == 0) {
            printf("Invalid arguments");
            cvReleaseImage(&DispImage);
            return;
        }
 
        // Find the width and height of the image
        x = img->width;
        y = img->height;
 
        // Find whether height or width is greater in order to resize the image
        max = (x > y)? x: y;
 
        // Find the scaling factor to resize the image
        scale = (float) ( (float) max / size );
 
        // Used to Align the images
        if( i % w == 0 && m!= 20) {
            m = 20;
            n+= 20 + size;
        }
        // Set the image ROI to display the current image
        cvSetImageROI(DispImage, cvRect(m, n, (int)( x/scale ), (int)( y/scale )));
 
        // Resize the input image and copy the it to the Single Big Image
        cvResize(img, DispImage);
 
        // Reset the ROI in order to display the next image
        cvResetImageROI(DispImage);
    }
 
    struct tm *tm;
    time_t t;
    char str_time[100];
    char compfile[100];
    char label[200];
     
    t = time(NULL);
    tm = localtime(&t);
     
    // Get the timestamp for file name and to mark images
    strftime(str_time, sizeof(str_time), "%Y-%m-%dHR%HMIN%M", tm);
    strftime(label, sizeof(str_time), "%Y-%m-%d %H:%M", tm);
    strcpy(compfile,"../timelapse/comp");
    strcat(compfile,str_time);
    strcat(compfile,".jpg");
    // Write to the image the timestamp
    CvFont font;
    double hScale=1.0;
    double vScale=1.0;
    int    lineWidth=1;
    cvInitFont(&font,CV_FONT_HERSHEY_SIMPLEX|CV_FONT_ITALIC, hScale,vScale,0,lineWidth);
    cvPutText (DispImage,label,cvPoint(200,450), &font, cvScalar(255,255,0));
    // This is the composite image
    cvSaveImage(compfile ,DispImage); 
    // End the number of arguments
    va_end(args);
    // Release the Image Memory
    cvReleaseImage(&DispImage);
}
 
/*
Old capture stuff
*/
int main( int argc, const char** argv ) {
    char i_str[5];
    char fname[300];
    int numCameras = 6;
    // Must keep facetime closed!!
    // To avoid a block, get each image, save to disk, then make composite
    for (int i = 0; i < numCameras; ++i) {
          sprintf(i_str, "%d", (i));
          strcpy(fname,"../timelapse/camera");
          strcat(fname,i_str);
          strcat(fname,".jpg");
          cout<< "fname: "<<fname <<endl;
          // Capture the Image from the webcam
          CvCapture *pCapturedImage = cvCreateCameraCapture(i);
          cout << "sleeping a minute" << endl;
          unsigned int sleep(50);
          IplImage *pSaveImg = cvQueryFrame(pCapturedImage);
          // Save the frame into a file
          cvSaveImage(fname ,pSaveImg); 
          cvReleaseCapture(&pCapturedImage);
     }
    IplImage *img0 = cvLoadImage("../timelapse/camera0.jpg");
    IplImage *img1 = cvLoadImage("../timelapse/camera1.jpg");
    IplImage *img2 = cvLoadImage("../timelapse/camera2.jpg");
    IplImage *img3 = cvLoadImage("../timelapse/camera3.jpg");
    IplImage *img4 = cvLoadImage("../timelapse/camera4.jpg");
    IplImage *img5 = cvLoadImage("../timelapse/camera5.jpg");
    cvShowManyImages("Image", 6, img0, img1, img2, img3, img4, img5);
}
