# SLIC-animator

The slic_animator.py script processes a video by applying the SLIC (Simple Linear Iterative Clustering) segmentation algorithm to its keyframes to generate a painting-like stylized version of the input video. To use it, call the video2slic function.

The video [UEFA EURO 2024 intro made with slic-animator](https://youtu.be/X2xzIweTNFM) attempts to imitate the [UEFA Euro 2024 introduction video](https://www.youtube.com/watch?v=pCPPEngwwCA). It is the video2slic output for the [UEFA Euro 2024 introduction video but with its original clips](https://www.youtube.com/watch?v=EajniExuHTw). In this case, video2slic was executed with its default parameters except for step (3 instead of 5). The input video had a resolution of 1280x720, 60 fps, and a duration of 30 seconds. The execution time was about 40 minutes (using only 3 cores on my at least 10-year-old HP laptop). Future improvements aim to enhance program efficiency through GPU acceleration and the use of OpenCV's slic function, which is better optimized. It is also planned to add a parameter that, if set to True, allows the user to keep the original audio of the video.

### Considerations:

- Parallel processing: using ThreadPoolExecutor allows leveraging multiple CPU cores, reducing processing time. However, the improvement depends on the available hardware.

- Output codec: avc1 codec is used to ensure compatibility with the MP4 format. If another format is required, the parameter in VideoWriter must be modified.

- Execution time: the tqdm library is used to inform the user of the estimated execution time. If the input video is computationally expensive (see "video2slic parameters" and "regarding the input video" below), it is normal for the progress bar and other indicators to take a few minutes to appear.

### video2slic parameters:

- input_path, output_path: input video path and output save path.

- n_segments: determines the number of superpixels (segments) to obtain. Increasing this value improves segmentation detail but increases processing time.

- compactness: controls the balance between color similarity and spatial proximity. Higher values generate more compact and regular segments; modifying this parameter can affect both the visual result and performance.

- sigma: applies pre-segmentation smoothing. A higher sigma can help homogenize regions, removing noise and impurities from the original video, though it also increases computation time.

- step: defines the interval between keyframes (default is 5). Lower values result in more processed keyframes, improving the final video’s visual smoothness but significantly increasing processing time, and vice versa.

### Regarding the input video:

- High-resolution videos require more time and resources to process each frame.

- A video with a higher FPS will have more total frames, influencing overall processing time, even considering that only keyframes are processed.

- Long videos contain more frames to read and write, affecting both performance and system resource usage.
