import cv2
import numpy as np
from skimage.segmentation import slic
from skimage.color import label2rgb
from skimage.util import img_as_ubyte
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os

def process_frame(frame, n_segments, compactness, sigma):
    try:
        frame_rgb = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2RGB)
        segments = slic(
            frame_rgb,
            n_segments=n_segments,
            compactness=compactness,
            sigma=sigma,
            channel_axis=-1,
            enforce_connectivity=False,
            start_label=0
        )
        pixelated = label2rgb(segments, frame_rgb, kind='avg', bg_label=-1)
        return cv2.cvtColor(img_as_ubyte(pixelated), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error procesando frame: {str(e)}")
        return None

def video2slic(input_path, output_path, step=5, n_segments=500, compactness=5, sigma=1):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Error al abrir el video de entrada")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Parámetros del video: {width}x{height} / {fps:.2f} fps")
    
    keyframe_indices = list(range(0, total_frames, step))
    keyframes = []
    for idx in keyframe_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            keyframes.append(frame.copy())

    wrkrs = min((os.cpu_count() or 4)-1,  len(keyframes), 16)
    processed = []
    with ThreadPoolExecutor(max_workers=wrkrs) as executor:
        process_func = partial(
            process_frame,
            n_segments=n_segments,
            compactness=compactness,
            sigma=sigma
        )
        
        futures = [executor.submit(process_func, frame) for frame in keyframes]
        
        with tqdm(total=len(futures), desc="Procesando keyframes") as pbar:
            for future in futures:
                result = future.result()
                if result is not None:
                    if result.shape == (height, width, 3):
                        processed.append(result)
                    else:
                        print("Error: Dimensiones incorrectas en frame procesado")
                pbar.update(1)

    fourcc = cv2.VideoWriter_fourcc(*'avc1') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        raise ValueError("Error al crear el archivo de salida")

    # Generar y escribir frames
    written_frames = 0
    with tqdm(total=total_frames, desc="Generando video") as pbar:
        for i, frame in enumerate(processed):
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            
            repeat = step if i < len(processed)-1 else total_frames - (i*step)
            
            # Escribir frame repetido correctamente
            for _ in range(repeat):
                out.write(frame)
                written_frames += 1
                pbar.update(1)
                
    print(f"\nFrames escritos: {written_frames}/{total_frames}")

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    original_path = "./euro_real.mp4"
    slic_path = "./euro_slic.mp4"
    video2slic(input_path=original_path, output_path=slic_path, step=3)