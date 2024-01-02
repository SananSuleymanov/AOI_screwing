# Automatic Optical Inspection for Screwing process

The project is intended to be used in manufacturing for the quality check of screwing process. It uses CNN based segmentation model which is trained on screwed and non-screwed images of product holes. 
Desktop application is developed using PyQT which allows users to create recipes for each product and also, run model in live-stream video which is captured using USB camera. The recipe consists of the drawn region of interests and is saved in JSON format for each screwing hole together with the product position, which is detected using the Foreground Extraction GrabCut algorithm. 
When the user selects the recipe from the dropdown menu and clicks on the "Start" button, it automatically runs the model in each cropped image from the region of interests received from JSON data.

If classification accuracy is over the threshold it will write "Pass" and screwing holes will be drawn using the green marker. If not, then "Fail" will be written on the screen and the rectangles will be marked using a red marker. All steps are recorded in the below-mentioned video.

Note: The code of the project is not public.
https://github.com/SananSuleymanov/AOI_screwing/assets/92025504/4e4bce93-7a0c-4a35-b2fa-7e0d33e35a60

