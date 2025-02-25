from .get_blink_rate import get_blinking_count

def get_score(video_path: str, iter_for_maxs: int):
    blink_rate = get_blinking_count(video_path=video_path, iter_for_maxs=iter_for_maxs)
    points = 0
    if 14 <= blink_rate <= 20:
        points += 1
    elif blink_rate < 7 or blink_rate > 27:
        points -= 1
    return blink_rate, points