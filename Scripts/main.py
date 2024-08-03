import sys

sys.path.append("../")

from rzd_detector.lib.codemodules.face.pulse.pulse import get_bpm_with_pbv  # noqa: E402


result = get_bpm_with_pbv("Scripts/test_files/pulse/zlata83.mp4")
