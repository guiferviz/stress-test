import io

import numpy as np
from PIL import Image
from jina.executors.crafters import BaseSegmenter

from io_bound.gif_reader import get_frames


class GifPreprocessor(BaseSegmenter):
    def __init__(self, img_shape: int = 96, every_k_frame: int = 1, max_frame: int = None, from_bytes: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img_shape = img_shape
        self.every_k_frame = every_k_frame
        self.max_frame = max_frame
        self.from_bytes = from_bytes

    def craft(self, raw_bytes, doc_id):
        result = []
        try:
            if self.from_bytes:
                im = Image.open(io.BytesIO(raw_bytes))
            else:
                im = Image.open(raw_bytes.decode())
            idx = 0
            for frame in get_frames(im):
                try:
                    if idx % self.every_k_frame == 0 and (
                            (self.max_frame is not None and idx < self.max_frame) or self.max_frame is None):
                        new_frame = frame.convert('RGB').resize([self.img_shape, ] * 2)
                        img = (np.array(new_frame) / 255).astype(np.float32)
                        # build chunk next, if the previous fail, then no chunk will be add
                        result.append(dict(doc_id=doc_id, offset=idx,
                                           weight=1., blob=img))
                except Exception as ex:
                    self.logger.error(ex)
                finally:
                    idx = idx + 1

            return result

        except Exception as ex:
            self.logger.error(ex)
