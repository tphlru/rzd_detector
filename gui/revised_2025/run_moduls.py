# emotions - :(
# pulse - ✓
# respiration - ✓ (нет экстраполяции)
# blinking - ✓
# voice - 
import subprocess
import timeit
import cv2
import logging
logger = logging.getLogger(__name__)

def run():
    print("Предупреждение: Компания Meta признана экстримисткой организацией и запрещена в РФ. Используются только открытые, некоммерческие технологии.")
    t = timeit.default_timer()
    # video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_count*0.3))
    subprocess.Popen(['python', 'gui/revised_2025/run_pulse.py'])
    subprocess.Popen(['python', 'gui/revised_2025/run_resp.py'])
    subprocess.Popen(['python', 'gui/revised_2025/run_blinking.py'])
    subprocess.Popen(['python', 'gui/revised_2025/run_emotions.py'])
    logger.info("Завершено, время предсказания значений:", timeit.default_timer() - t)
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.error(e)