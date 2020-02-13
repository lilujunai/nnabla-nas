import numpy as np
import nnabla.functions as F
import nnabla as nn


class Normalizer(object):
    r"""Normalize a input image with mean and standard deviation.

    Given mean: ``(M1,...,Mn)`` and std: ``(S1,..,Sn)`` for ``n`` channels,
    this transform will normalize each channel of the input image i.e.
    ``input[channel] = (input[channel] - mean[channel]) / std[channel]``

    Args:
        mean (sequence): Sequence of means for each channel.
        std (sequence): Sequence of standard deviations for each channel.
    """

    def __init__(self, mean, std, scale):
        self._mean = nn.Variable.from_numpy_array(
            np.reshape(mean, (1, 3, 1, 1)))
        self._std = nn.Variable.from_numpy_array(
            np.reshape(std, (1, 3, 1, 1)))
        self._scale = scale

    def __call__(self, input):
        out = F.mul_scalar(input, self._scale)
        out = F.sub2(input, self._mean)
        out = F.div2(out, self._std)
        return out

    def __str__(self):
        return self.__class__.__name__
        + f'(mean={self._mean.d}, std={self._std.d}, scale={self._scale})'


class Compose(object):
    r"""Composes several transforms together.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to
            compose.
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for t in self.transforms:
            img = t(img)
        return img

    def append(self, transform):
        r"""Appends a transfomer to the end.

        Args:
            transform (Transformer): The transformer to append.
        """
        self.transforms.append(transform)

    def __str__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string


class Cutout(object):
    r"""Cutout layer.

    Cutout is a simple regularization technique for convolutional neural
    networks that involves removing contiguous sections of input images,
    effectively augmenting the dataset with partially occluded versions of
    existing samples.

    Args:
        length (int): The lenth of region, which will be cutout.

    References:
        [1] DeVries, Terrance, and Graham W. Taylor. "Improved regularization
                of convolutional neural networks with cutout." arXiv preprint
                arXiv:1708.04552 (2017).
    """

    def __init__(self, length):
        self._length = length

    def __call__(self, image):
        h, w = image.shape[2:]
        mask = np.ones((h, w), np.float32)
        y = np.random.randint(h)
        x = np.random.randint(w)
        y1 = np.clip(y - self._length // 2, 0, h)
        y2 = np.clip(y + self._length // 2, 0, h)
        x1 = np.clip(x - self._length // 2, 0, w)
        x2 = np.clip(x + self._length // 2, 0, w)
        mask[y1: y2, x1: x2] = 0.
        image *= mask
        return image

    def __str__(self):
        return self.__class__.__name__ + f'(length={self._length})'


class Resize(object):
    r"""Resize an ND array with interpolation.

    Args:
        size (tuple of `int`): The output sizes for axes. If this is
            given, the scale factors are determined by the output sizes and the
            input sizes.
        interpolation (str): Interpolation mode chosen from
            ('linear'|'nearest'). The default is 'linear'.
    """

    def __init__(self, size, interpolation='linear'):
        self._size = size
        self._interpolation = interpolation

    def __call__(self, input):
        out = F.interpolate(input, output_size=self._size,
                            mode=self._interpolation)
        return out

    def __str__(self):
        return (self.__class__.__name__
                + f'(size={self._size}, interpolation={self._interpolation})')


class CenterCrop(object):
    def __init__(self):
        pass


class RandomCrop(object):
    def __init__(self):
        super().__init__()


class RandomHorizontalFlip(object):
    def __init__(self):
        super().__init__()


class RandomRotation(object):
    def __init__(self):
        super().__init__()


class RandomVerticalFlip(object):
    def __init__(self):
        super().__init__()


class Lambda(object):
    r"""Apply a user-defined lambda as a transform.

    Args:
        func (function): Lambda/function to be used for transform.
    """

    def __init__(self, func):
        assert callable(func), repr(type(func).__name__) + \
            " object is not callable"
        self._func = func

    def __call__(self, input):
        return self._func(input)

    def __str__(self):
        return self.__class__.__name__ + '()'
