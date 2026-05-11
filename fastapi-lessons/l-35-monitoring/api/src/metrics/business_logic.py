from prometheus_client import Counter

from src.metrics.container.collector_container import RegistryContainer

# --- Auth ---

user_logins_total = Counter(
    'user_logins_total',
    'Total number of user logins',
    registry=RegistryContainer.registry()
)

user_logins_succeed_total = Counter(
    'user_logins_succeed_total',
    'Total number of successful user logins',
    registry=RegistryContainer.registry()
)

# --- operations with files ---

joke_get_total = Counter(
    'joke_get_total',
    'Total number of GET requests for "/joke" endpoints',
    registry=RegistryContainer.registry()
)

meme_get_total = Counter(
    'meme_get_total',
    'Total number of GET requests for "/meme" endpoints',
    registry=RegistryContainer.registry()
)
