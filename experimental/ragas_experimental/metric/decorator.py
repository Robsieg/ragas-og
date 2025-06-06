"""decorator factory for creating custom metrics"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/api/metric/decorator.ipynb.

# %% auto 0
__all__ = ['create_metric_decorator']

# %% ../../nbs/api/metric/decorator.ipynb 2
import typing as t
import inspect
import asyncio
from dataclasses import dataclass
from . import MetricResult
from ..llm import RagasLLM
from ..prompt.base import Prompt


def create_metric_decorator(metric_class):
    """
    Factory function that creates decorator factories for different metric types.

    Args:
        metric_class: The metric class to use (DiscreteMetrics, NumericMetrics, etc.)

    Returns:
        A decorator factory function for the specified metric type
    """

    def decorator_factory(
        llm: RagasLLM,
        prompt: t.Union[str, Prompt],
        name: t.Optional[str] = None,
        **metric_params,
    ):
        """
        Creates a decorator that wraps a function into a metric instance.

        Args:
            llm: The language model instance to use
            prompt: The prompt template
            name: Optional name for the metric (defaults to function name)
            **metric_params: Additional parameters specific to the metric type
                (values for DiscreteMetrics, range for NumericMetrics, etc.)

        Returns:
            A decorator function
        """

        def decorator(func):
            # Get metric name and check if function is async
            metric_name = name or func.__name__
            is_async = inspect.iscoroutinefunction(func)

            # TODO: Move to dataclass type implementation
            @dataclass
            class CustomMetric(metric_class):

                def _run_sync_in_async(self, func, *args, **kwargs):
                    """Run a synchronous function in an async context."""
                    # For sync functions, just run them normally
                    return func(*args, **kwargs)

                def _execute_metric(self, is_async_execution, reasoning, **kwargs):
                    """Execute the metric function with proper async handling."""
                    try:
                        if is_async:
                            # Async function implementation
                            if is_async_execution:
                                # In async context, await the function directly
                                result = func(self.llm, self.prompt, **kwargs)
                            else:
                                # In sync context, run the async function in an event loop
                                try:
                                    loop = asyncio.get_event_loop()
                                except RuntimeError:
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                result = loop.run_until_complete(
                                    func(self.llm, self.prompt, **kwargs)
                                )
                        else:
                            # Sync function implementation
                            result = func(self.llm, self.prompt, **kwargs)

                        return result
                    except Exception as e:
                        # Handle errors gracefully
                        error_msg = f"Error executing metric {self.name}: {str(e)}"
                        return MetricResult(result=None, reason=error_msg)

                def score(self, reasoning: bool = True, n: int = 1, **kwargs):
                    """Synchronous scoring method."""
                    return self._execute_metric(
                        is_async_execution=False, reasoning=reasoning, **kwargs
                    )

                async def ascore(self, reasoning: bool = True, n: int = 1, **kwargs):
                    """Asynchronous scoring method."""
                    if is_async:
                        # For async functions, await the result
                        result = await func(self.llm, self.prompt, **kwargs)
                        return self._extract_result(result, reasoning)
                    else:
                        # For sync functions, run normally
                        result = self._run_sync_in_async(
                            func, self.llm, self.prompt, **kwargs
                        )
                        return result

            # Create the metric instance with all parameters
            metric_instance = CustomMetric(
                name=metric_name, prompt=prompt, llm=llm, **metric_params
            )

            # Preserve metadata
            metric_instance.__name__ = metric_name
            metric_instance.__doc__ = func.__doc__

            return metric_instance

        return decorator

    return decorator_factory
