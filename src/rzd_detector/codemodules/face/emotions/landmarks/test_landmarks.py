import cv2
import pprint
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor


def main():
    image_path = "src/rzd_detector/codemodules/face/emotions/dev/supernet/datasets/expw/origin/afraid_African_960.jpg"
    processor = FaceLandmarksProcessor(verbose=True)

    # Process the image
    processor.process_landmarks(
        image_path,
        save_path="src/rzd_detector/codemodules/face/emotions/dev/face.jpg",
        return_raw=False,
        hide_eyes=False,
        hide_mouth=False,
        transparent_bg=True,
        curve_crop=False,
    )

    # if result is None:
    #     print("No face landmarks detected.")
    #     return

    # # Display the processed image
    # processed_image = result.processed_image
    # cv2.imshow("Processed Image", processed_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # # Pretty print the coordinates of the landmarks
    # coordinates = result.landmarks
    # print("Landmark Coordinates:")
    # pprint.pprint(coordinates)

    # result.save_image("src/rzd_detector/codemodules/face/emotions/dev/face.png")

    # Get and display the full mask
    # full_mask = result.get_full_mask()
    # if full_mask is not None:
    #     cv2.imshow("Full Mask", full_mask)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
