from gh_profile_repo_pins.repo_pins_exceptions import RepoPinImageMediaError
import gh_profile_repo_pins.repo_pins_enum as enums
from gh_profile_repo_pins.utils import load_img
from PIL import Image as im, ImageOps as im_ops
from requests import get, Response, HTTPError
from urllib.parse import urlparse
from base64 import b64encode
from cairosvg import svg2png
from io import BytesIO


class RepoPinImgMedia:

    __DEFAULT_ALIGN: str = "xMidYMid"
    __DEFAULT_MODE: str = "stretch"
    __DEFAULT_OPACITY: float = 0.25

    __BASE_64_ENCODING: str = "ascii"
    __RES_MIME_HEADER: str = "Content-Type"
    __IMG_DIMS: int = 1600
    __IMG_QUALITY: int = 80
    __IMG_COMPRESSION: int = 6

    def __init__(
        self,
        img: str = None,
        align: str = __DEFAULT_ALIGN,
        mode: str = __DEFAULT_MODE,
        opacity: float = __DEFAULT_OPACITY,
    ) -> None:
        self.__bg_img: bytes | str = img
        self.__bg_img_mime: enums.RepoPinsImgMediaBgImgMime = (
            enums.RepoPinsImgMediaBgImgMime.PNG
        )
        self.__bg_img_align: enums.RepoPinsImgMediaBgImgAlign = (
            enums.RepoPinsImgMediaBgImgAlign(align.lower())
            if align and align.lower() in enums.RepoPinsImgMediaBgImgAlign
            else enums.RepoPinsImgMediaBgImgAlign(self.__DEFAULT_ALIGN.lower())
        )
        self.__bg_img_mode: enums.RepoPinsImgMediaBgImgMode = (
            enums.RepoPinsImgMediaBgImgMode(mode.lower())
            if mode
            else enums.RepoPinsImgMediaBgImgMode(self.__DEFAULT_MODE.lower())
        )
        self.__bg_img_opacity: float = (
            opacity
            if opacity is not None and 0.0 <= opacity <= 1.0
            else self.__DEFAULT_OPACITY
        )
        self.__bg_img_encoded_url: str | None = None

    def __repr__(self) -> str:
        return (
            f"img: {self.__bg_img}\n"
            f"align: {self.__bg_img_align}\n"
            f"mode: {self.__bg_img_mode}\n"
            f"opacity: {self.__bg_img_opacity}\n"
            f"encoded URL: {self.__bg_img_encoded_url}\n"
        )

    def __is_img_url(self) -> bool:
        return bool(urlparse(url=self.__bg_img).scheme)

    def __decode_img(self, byte_img: bytes) -> im.Image:
        if self.__bg_img_mime == enums.RepoPinsImgMediaBgImgMime.SVG:
            raw_conversion: BytesIO = BytesIO()
            svg2png(bytestring=byte_img, write_to=raw_conversion)
            raw_conversion.seek(0)
            return im.open(fp=raw_conversion)
        return im.open(fp=BytesIO(initial_bytes=byte_img))

    def __format_encoded_img(self, byte_img: bytes) -> bytes:
        img_encoder: im.Image = im_ops.exif_transpose(
            image=self.__decode_img(byte_img=byte_img)
        )
        img_encoder.thumbnail(size=(self.__IMG_DIMS, self.__IMG_DIMS))

        self.__bg_img_mime = enums.RepoPinsImgMediaBgImgMime.WEB
        encoded_img: BytesIO = BytesIO()
        img_encoder.save(
            fp=encoded_img,
            format=self.__bg_img_mime.value.split("/")[-1].upper(),
            quality=self.__IMG_QUALITY,
            method=self.__IMG_COMPRESSION,
        )
        return encoded_img.getvalue()

    def __set_encoded_url(self, encoded_url: str) -> None:
        self.__bg_img_encoded_url = (
            f"data:{self.__bg_img_mime.value.lower()};base64,{encoded_url}"
        )

    def __load_url(self) -> None:
        try:
            res: Response = get(url=self.__bg_img, timeout=5)
            res.raise_for_status()
        except HTTPError:
            raise RepoPinImageMediaError(
                msg="HTTP error attempting to fetch background image URL."
            )
        self.__bg_img_mime = enums.RepoPinsImgMediaBgImgMime(
            res.headers.get(self.__RES_MIME_HEADER, self.__bg_img_mime.value).lower()
        )
        self.__set_encoded_url(
            encoded_url=b64encode(
                s=self.__format_encoded_img(byte_img=res.content)
            ).decode(encoding=self.__BASE_64_ENCODING)
        )

    def __load_file(self) -> None:
        try:
            self.__bg_img_mime = enums.RepoPinsImgMediaBgImgMime(
                [
                    e.value
                    for e in enums.RepoPinsImgMediaBgImgMime
                    if self.__bg_img.split(".")[-1][:2].upper() == e.name[:2]
                ][0]
            )
        except IndexError:
            raise RepoPinImageMediaError(
                msg=f"Invalid image type. "
                f"Use one of the valid types: {list(enums.RepoPinsImgMediaBgImgMime.__members__.keys())}."
            )

        try:
            self.__bg_img = load_img(img_path=self.__bg_img)
        except FileNotFoundError:
            raise RepoPinImageMediaError(msg="Background image file not found.")
        self.__set_encoded_url(
            encoded_url=b64encode(
                s=self.__format_encoded_img(byte_img=self.__bg_img)
            ).decode(encoding=self.__BASE_64_ENCODING)
        )

    @property
    def align(self) -> enums.RepoPinsImgMediaBgImgAlign:
        return self.__bg_img_align

    @property
    def mode(self) -> enums.RepoPinsImgMediaBgImgMode:
        return self.__bg_img_mode

    @property
    def opacity(self) -> float:
        return self.__bg_img_opacity

    @property
    def encoded_url(self) -> str | None:
        return self.__bg_img_encoded_url

    def load(self) -> None:
        if self.__bg_img:
            if self.__is_img_url():
                self.__load_url()
            elif self.__bg_img.startswith("data:"):
                self.__bg_img_encoded_url = self.__bg_img
            else:
                self.__load_file()
