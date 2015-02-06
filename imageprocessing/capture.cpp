#include <opencv2/objdetect/objdetect.hpp>
#include "highgui.h"
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <unistd.h>
#include <iostream>
#include <stdio.h>
#include <cstdlib>
using namespace std;
using namespace cv;
// Captures images from each camera.  Facetime and other camera software
// must NOT be running or this program can't get to the cameras.
 
int main( int argc, const char** argv )
{
    // CvCapture* capture = 0;
    Mat frame, frameCopy, image, altframe;
    char i_str[5];
    char fname[300];
 
    cout << "starting" << endl;
       int j=0; // AV foundation offset also try 500
    // Must keep facetime closed!!
    for (int i = 0; i < 6; ++i) {
          sprintf(i_str, "%d", (i+j));
          strcpy(fname,"../currentState/camera");
          strcat(fname,i_str);
          strcat(fname,".jpg");
          cout<< "fname: "<<fname <<endl;
          // Capture the Image from the webcam
          CvCapture *pCapturedImage = cvCreateCameraCapture(i+j);
          cout << "sleeping a minute" << endl;
          unsigned int sleep(50);
           
          // Get the frame
          IplImage *pSaveImg = cvQueryFrame(pCapturedImage);
           
          // Save the frame into a file
          cvSaveImage(fname ,pSaveImg); 
          cvReleaseCapture(&pCapturedImage);
     }
/*
    if(!capture) cout << "No camera detected" << endl;
 
    cvNamedWindow( "result", 1 );
 
    if( capture )
    {
        cout << "In capture ..." << endl;
        for(;;)
        {
            cout << "before query frame" << endl;
            IplImage* iplImg = cvQueryFrame( capture );
            cout << "before ipImg" << endl;
            frame = iplImg;
            if( frame.empty() )
                break;
            if( iplImg->origin == IPL_ORIGIN_TL )
                frame.copyTo( frameCopy );
            else
                flip( frame, frameCopy, 0 );
 
            cout << "before waitkey" << endl;
            if( waitKey( 10 ) >= 0 )
                cvReleaseCapture( &capture );
        }
 
        waitKey(0);
 
    cvDestroyWindow("result");
 
    return 0;
    }
*/
}
