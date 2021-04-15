import os

_type_dict = {
    "SPI_VERSION": str,
    "SPI_DRIVE_LABEL": str,
    "SPI_IMAGE_DIR": str,
    "SPI_METADATA_FILENAME": str,
    "SPI_IM_W": int,
    "SPI_IM_H": int,
    "SPI_LIGHT_SENSOR_W": int,
    "SPI_LIGHT_SENSOR_H": int,
    "SPI_ZOOM_X": float,
    "SPI_ZOOM_Y": float,
    "SPI_ZOOM_W": float,
    "SPI_ZOOM_H": float,
    "SPI_AWB_RED": int,
    "SPI_AWB_BLUE": int,
    "SPI_OFF_GPIO": int,  # set high to send poweroff?
    "SPI_DHT_GPIO": int,
    "SPI_FLASH_GPIO": int,
    "SPI_DHT": str,
    "SPI_DHT_TIMEOUT": int,
    "SPI_IM_JPEG_QUALITY": int
}


class ConfigHandler(dict):
    def __init__(self):
        super().__init__()
        for k, t in _type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]