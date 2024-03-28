from pathlib import Path
from matplotlib.image import imread, imsave


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        if self.data is None:
            raise RuntimeError("No image data to process.")

        height = len(self.data)
        width = len(self.data[0])

        # Rotate the image data clockwise
        rotated_data = [[0] * height for _ in range(width)]
        for i in range(width):
            for j in range(height):
                rotated_data[i][j] = self.data[height - j - 1][i]

        self.data = rotated_data

    def counter_rotate(self):
        if self.data is None:
            raise RuntimeError("No image data to process.")

        height = len(self.data)
        width = len(self.data[0])

        # Rotate the image data counterclockwise
        rotated_data = [[0] * height for _ in range(width)]
        for i in range(width):
            for j in range(height):
                rotated_data[i][j] = self.data[j][width - i - 1]

        self.data = rotated_data

    def concat(self, other_img, direction='horizontal'):
        if self.data is None or other_img.data is None:
            raise RuntimeError("No image data to process.")

        # Check compatibility of image dimensions for concatenation
        if direction == 'horizontal':
            if len(self.data) != len(other_img.data):
                raise RuntimeError("Images have different heights. Cannot concatenate horizontally.")
            concatenated_data = [self.data[i] + other_img.data[i] for i in range(len(self.data))]
        else:  # vertical concatenation
            if len(self.data[0]) != len(other_img.data[0]):
                raise RuntimeError("Images have different widths. Cannot concatenate vertically.")
            concatenated_data = self.data + other_img.data

        # Update image data with concatenated image
        self.data = concatenated_data

    def salt_n_pepper(self):
        """
        Add salt and pepper noise to the image.
        """
        if self.data is None:
            raise RuntimeError("No image data to process.")

        import random

        for i in range(len(self.data)):
            for j in range(len(self.data[0])):
                rand = random.random()
                if rand < 0.2:
                    self.data[i][j] = 0  # Pepper noise (black)
                elif rand > 0.8:
                    self.data[i][j] = 255  # Salt noise (white)

    def segment(self):
        """
        Segment the image into meaningful parts.
        """
        if self.data is None:
            raise RuntimeError("No image data to process.")

        for i in range(len(self.data)):
            for j in range(len(self.data[0])):
                if self.data[i][j] > 100:
                    self.data[i][j] = 255  # White
                else:
                    self.data[i][j] = 0  # Black


