"""Methods to create and manage datasets within projects"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/api/project/datasets.ipynb.

# %% auto 0
__all__ = ['create_dataset_columns', 'get_dataset_from_ragas_app', 'get_dataset_from_local']

# %% ../../nbs/api/project/datasets.ipynb 3
import typing as t
import os
import asyncio
import tempfile

from fastcore.utils import patch
from pydantic import BaseModel

from .core import Project
from ..typing import SUPPORTED_BACKENDS
from ..backends.factory import RagasApiClientFactory
from ..backends.ragas_api_client import RagasApiClient
import ragas_experimental.typing as rt
from ..utils import async_to_sync, create_nano_id
from ..dataset import Dataset
from ..utils import get_test_directory

# %% ../../nbs/api/project/datasets.ipynb 4
async def create_dataset_columns(
    project_id, dataset_id, columns, create_dataset_column_func
):
    tasks = []
    for column in columns:
        tasks.append(
            create_dataset_column_func(
                project_id=project_id,
                dataset_id=dataset_id,
                id=create_nano_id(),
                name=column["name"],
                type=column["type"],
                settings=column["settings"],
            )
        )
    return await asyncio.gather(*tasks)

# %% ../../nbs/api/project/datasets.ipynb 5
def get_dataset_from_ragas_app(
    self: Project, name: str, model: t.Type[BaseModel]
) -> Dataset:
    """Create a dataset in the Ragas App backend."""
    # create the dataset
    sync_version = async_to_sync(self._ragas_api_client.create_dataset)
    dataset_info = sync_version(
        project_id=self.project_id,
        name=name if name is not None else model.__name__,
    )

    # create the columns for the dataset
    column_types = rt.ModelConverter.model_to_columns(model)
    sync_version = async_to_sync(create_dataset_columns)
    sync_version(
        project_id=self.project_id,
        dataset_id=dataset_info["id"],
        columns=column_types,
        create_dataset_column_func=self._ragas_api_client.create_dataset_column,
    )

    # Return a new Dataset instance
    return Dataset(
        name=name if name is not None else model.__name__,
        model=model,
        datatable_type="datasets",
        project_id=self.project_id,
        dataset_id=dataset_info["id"],
        ragas_api_client=self._ragas_api_client,
        backend="ragas_app",
    )

# %% ../../nbs/api/project/datasets.ipynb 6
def get_dataset_from_local(
    self: Project, name: str, model: t.Type[BaseModel]
) -> Dataset:
    """Create a dataset in the local filesystem backend.

    Args:
        name: Name of the dataset
        model: Pydantic model defining the structure

    Returns:
        Dataset: A new dataset configured to use the local backend
    """
    # Use a UUID as the dataset ID
    dataset_id = create_nano_id()

    # Return a new Dataset instance with local backend
    return Dataset(
        name=name if name is not None else model.__name__,
        model=model,
        datatable_type="datasets",
        project_id=self.project_id,
        dataset_id=dataset_id,
        backend="local",
        local_root_dir=os.path.dirname(self._root_dir),  # Root dir for all projects
    )

# %% ../../nbs/api/project/datasets.ipynb 7
@patch
def create_dataset(
    self: Project,
    model: t.Type[BaseModel],
    name: t.Optional[str] = None,
    backend: t.Optional[SUPPORTED_BACKENDS] = None,
) -> Dataset:
    """Create a new dataset.

    Args:
        model: Model class defining the dataset structure
        name: Name of the dataset (defaults to model name if not provided)
        backend: The backend to use (defaults to project's backend if not specified)

    Returns:
        Dataset: A new dataset object for managing entries
    """
    # If name is not provided, use the model name
    if name is None:
        name = model.__name__

    # If backend is not specified, use the project's backend
    if backend is None:
        backend = self.backend

    # Create dataset using the appropriate backend
    if backend == "local":
        return get_dataset_from_local(self, name, model)
    elif backend == "ragas_app":
        return get_dataset_from_ragas_app(self, name, model)
    else:
        raise ValueError(f"Unsupported backend: {backend}")

# %% ../../nbs/api/project/datasets.ipynb 16
@patch
def get_dataset_by_id(
    self: Project,
    dataset_id: str,
    model: t.Type[BaseModel],
    backend: t.Optional[SUPPORTED_BACKENDS] = None,
) -> Dataset:
    """Get an existing dataset by ID.

    Args:
        dataset_id: The ID of the dataset to retrieve
        model: The model class to use for the dataset entries
        backend: The backend to use (defaults to project's backend)

    Returns:
        Dataset: The retrieved dataset
    """
    # If backend is not specified, use the project's backend
    if backend is None:
        backend = self.backend

    if backend == "ragas_app":
        # Search for database with given ID
        sync_version = async_to_sync(self._ragas_api_client.get_dataset)
        dataset_info = sync_version(project_id=self.project_id, dataset_id=dataset_id)

        # For now, return Dataset without model type
        return Dataset(
            name=dataset_info["name"],
            model=model,
            datatable_type="datasets",
            project_id=self.project_id,
            dataset_id=dataset_id,
            ragas_api_client=self._ragas_api_client,
            backend="ragas_app",
        )
    elif backend == "local":
        # For local backend, this is not a typical operation since we use names
        # We could maintain a mapping of IDs to names, but for now just raise an error
        raise NotImplementedError(
            "get_dataset_by_id is not implemented for local backend. "
            "Use get_dataset with the dataset name instead."
        )
    else:
        raise ValueError(f"Unsupported backend: {backend}")

# %% ../../nbs/api/project/datasets.ipynb 17
@patch
def get_dataset(
    self: Project,
    dataset_name: str,
    model: t.Type[BaseModel],
    backend: t.Optional[SUPPORTED_BACKENDS] = None,
) -> Dataset:
    """Get an existing dataset by name.

    Args:
        dataset_name: The name of the dataset to retrieve
        model: The model class to use for the dataset entries
        backend: The backend to use (defaults to project's backend if not specified)

    Returns:
        Dataset: The retrieved dataset
    """
    # If backend is not specified, use the project's backend
    if backend is None:
        backend = self.backend

    if backend == "ragas_app":
        # Search for dataset with given name
        sync_version = async_to_sync(self._ragas_api_client.get_dataset_by_name)
        dataset_info = sync_version(
            project_id=self.project_id, dataset_name=dataset_name
        )

        # Return Dataset instance
        return Dataset(
            name=dataset_info["name"],
            model=model,
            datatable_type="datasets",
            project_id=self.project_id,
            dataset_id=dataset_info["id"],
            ragas_api_client=self._ragas_api_client,
            backend="ragas_app",
        )
    elif backend == "local":
        # Check if the dataset file exists
        dataset_path = self.get_dataset_path(dataset_name)
        if not os.path.exists(dataset_path):
            raise ValueError(f"Dataset '{dataset_name}' does not exist")

        # Create dataset instance with a random ID
        dataset_id = create_nano_id()

        # Return Dataset instance
        return Dataset(
            name=dataset_name,
            model=model,
            datatable_type="datasets",
            project_id=self.project_id,
            dataset_id=dataset_id,
            backend="local",
            local_root_dir=os.path.dirname(self._root_dir),  # Root dir for all projects
        )
    else:
        raise ValueError(f"Unsupported backend: {backend}")

# %% ../../nbs/api/project/datasets.ipynb 18
@patch
def list_dataset_names(
    self: Project, backend: t.Optional[SUPPORTED_BACKENDS] = None
) -> t.List[str]:
    """List all datasets in the project.

    Args:
        backend: The backend to use (defaults to project's backend)

    Returns:
        List[str]: Names of all datasets in the project
    """
    # If backend is not specified, use the project's backend
    if backend is None:
        backend = self.backend

    if backend == "ragas_app":
        # Get all datasets from API
        sync_version = async_to_sync(self._ragas_api_client.list_datasets)
        datasets = sync_version(project_id=self.project_id)
        return [dataset["name"] for dataset in datasets]
    elif backend == "local":
        # Get all CSV files in the datasets directory
        datasets_dir = os.path.join(self._root_dir, "datasets")
        if not os.path.exists(datasets_dir):
            return []

        return [
            os.path.splitext(f)[0]
            for f in os.listdir(datasets_dir)
            if f.endswith(".csv")
        ]
    else:
        raise ValueError(f"Unsupported backend: {backend}")
