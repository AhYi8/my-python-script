import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser


class DateUtils:
    @staticmethod
    def get_current_date():
        """获取当前日期"""
        return datetime.now().date()

    @staticmethod
    def get_current_datetime():
        """获取当前日期时间"""
        return datetime.now()

    @staticmethod
    def get_current_datetime_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """返回当前日期时间字符串，格式: 2024-09-08 01:32:08"""
        return datetime.now().strftime(fmt)

    @staticmethod
    def str_to_date(date_str: str, fmt: str = "%Y-%m-%d") -> datetime.date:
        """将字符串转换为日期"""
        return datetime.strptime(date_str, fmt).date()

    @staticmethod
    def date_to_str(date: datetime.date, fmt: str = "%Y-%m-%d") -> str:
        """将日期转换为字符串"""
        return date.strftime(fmt)

    @staticmethod
    def datetime_to_str(date: datetime, fmt: str = "%Y-%m-%d %H:%M:%S"):
        return date.strftime(fmt)

    @staticmethod
    def iso_str_to_datetime(iso_str: str) -> datetime:
        """将带时区的 ISO 8601 格式时间字符串转换为 datetime 对象"""
        return parser.parse(iso_str)

    @staticmethod
    def add_days(date: datetime.date, days: int) -> datetime.date:
        """在指定日期基础上增加或减少天数"""
        return date + timedelta(days=days)

    @staticmethod
    def add_months(date: datetime.date, months: int) -> datetime.date:
        """在指定日期基础上增加或减少月份"""
        return date + relativedelta(months=months)

    @staticmethod
    def days_between(date1: datetime.date, date2: datetime.date) -> int:
        """计算两个日期之间的天数差"""
        return (date2 - date1).days

    @staticmethod
    def date_to_datetime(date_obj: datetime.date) -> datetime:
        """将 date 对象转换为 datetime 对象"""
        return datetime.combine(date_obj, datetime.min.time())

    @staticmethod
    def datetime_to_date(datetime_obj: datetime) -> datetime.date:
        """将 datetime 对象转换为 date 对象"""
        return datetime_obj.date()

    @staticmethod
    def is_valid_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
        """判断字符串是否为合法的日期格式"""
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_current_year():
        """获取当前年份"""
        return datetime.now().year

    @staticmethod
    def get_current_month():
        """获取当前月份"""
        return datetime.now().month

    @staticmethod
    def get_current_day():
        """获取当前日期中的日"""
        return datetime.now().day

    @staticmethod
    def get_timezone_aware_datetime(timezone_str: str = 'UTC'):
        """返回指定时区的当前时间"""
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)

    @staticmethod
    def is_before(date1: datetime, date2: datetime) -> bool:
        """判断 date1 是否在 date2 之前"""
        return date1 < date2

    @staticmethod
    def is_after(date1: datetime, date2: datetime) -> bool:
        """判断 date1 是否在 date2 之后"""
        return date1 > date2

    @staticmethod
    def is_same(date1: datetime, date2: datetime) -> bool:
        """判断 date1 和 date2 是否相同"""
        return date1 == date2

    @staticmethod
    def to_naive(datetime_obj: datetime) -> datetime:
        """将带时区的 datetime 转换为 naive datetime（移除时区信息）"""
        if datetime_obj.tzinfo is not None:
            return datetime_obj.replace(tzinfo=None)
        return datetime_obj