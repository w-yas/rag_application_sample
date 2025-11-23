import logging
import logging.config

from back.api.utils.add_request_id import get_request_id


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        # 1. 属性がレコードに存在しない場合
        if not hasattr(record, "request_id"):
            try:
                # 2. contextvar から現在のリクエストIDを取得する
                current_id = get_request_id()
                # 3. 取得した ID (またはデフォルト値) を設定する
                record.request_id = current_id
            except LookupError:
                # contextvar に値がセットされていない (リクエスト外の初期ログなど)
                record.request_id = "N/A"
        return True


request_id_filter_instance = RequestIDFilter()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            # 既に定義された RequestIDFilter インスタンスを使うための設定
            "()": lambda: request_id_filter_instance
        }
    },
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(name)s %(request_id)s %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bg_red",
            },
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": "INFO",
            "filters": ["request_id_filter"],
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
logging.config.dictConfig(LOGGING)


logger = logging.getLogger("api_logger")
