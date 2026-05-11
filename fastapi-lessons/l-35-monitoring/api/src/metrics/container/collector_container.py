from prometheus_client import CollectorRegistry


class RegistryContainer():
    _registry = None

    @classmethod
    def registry(cls) -> CollectorRegistry:
        if cls._registry is None:
            cls._registry = CollectorRegistry()
        return cls._registry
