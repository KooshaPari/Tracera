defmodule HexagonalProject.Domain.Ports.Inbound do
  @moduledoc """
  Inbound ports (use cases / services).
  """

  alias HexagonalProject.Domain.Entities.ExampleEntity

  @doc """
  Service port for managing example entities.
  """
  @callback create_example(String.t(), String.t(), String.t()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t()}

  @callback get_example(String.t()) ::
              {:ok, ExampleEntity.t()} | {:error, :not_found}

  @callback update_example(String.t(), map()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t() | :not_found}

  @callback delete_example(String.t()) ::
              :ok | {:error, :not_found}

  @callback list_examples() ::
              {:ok, [ExampleEntity.t()]} | {:error, String.t()}

  @callback activate_example(String.t()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t() | :not_found}

  @callback complete_example(String.t()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t() | :not_found}
end
