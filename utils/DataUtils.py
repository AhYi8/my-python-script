

class DataUtils:

    @classmethod
    def decode_bytes(cls, obj):
        if isinstance(obj, dict):
            return {DataUtils.decode_bytes(k): DataUtils.decode_bytes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DataUtils.decode_bytes(i) for i in obj]
        elif isinstance(obj, tuple):
            return tuple(DataUtils.decode_bytes(i) for i in obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        else:
            return obj