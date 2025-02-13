import cv2
import pprint
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor


def main():
    image_path = "/home/timur/Download/test4.jpg"
    processor = FaceLandmarksProcessor(verbose=True)

    # Process the image
    result = processor.process_landmarks(
        image_path, return_image=True, return_raw=True, mouth_k=1.5
    )

    if result is None:
        print("No face landmarks detected.")
        return

    # Display the processed image
    processed_image = result.processed_image
    cv2.imshow("Processed Image", processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Pretty print the coordinates of the landmarks
    coordinates = result.landmarks
    print("Landmark Coordinates:")
    pprint.pprint(coordinates)

    # Get and display the full mask
    full_mask = result.get_full_mask()
    if full_mask is not None:
        cv2.imshow("Full Mask", full_mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
