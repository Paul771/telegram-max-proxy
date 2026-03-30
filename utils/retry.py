import asyncio
from typing import TypeVar, Callable, Any
from functools import wraps
from utils.logger import setup_logger
from utils.constants import MAX_RETRIES, RETRY_DELAY, RETRY_BACKOFF

logger = setup_logger(__name__)

T = TypeVar('T')


def async_retry(
    max_retries: int = MAX_RETRIES,
    delay: float = RETRY_DELAY,
    backoff: float = RETRY_BACKOFF,
    exceptions: tuple = (Exception,)
):
    """
    Декоратор для повторных попыток выполнения асинхронной функции
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений для перехвата
    
    Example:
        @async_retry(max_retries=3, delay=1, backoff=2)
        async def fetch_data():
            # code that might fail
            pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}: {e}"
                        )
            
            # Если все попытки провалились, выбрасываем последнее исключение
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator
