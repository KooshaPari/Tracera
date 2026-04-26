defmodule HexagonalProject.Domain.Ports.Outbound do
  @moduledoc """
  Outbound ports (repository interfaces).
  """

  alias HexagonalProject.Domain.Entities.ExampleEntity

  @doc """
  Repository port for example entities.
  """
  @callback get_by_id(String.t()) ::
              {:ok, ExampleEntity.t()} | {:error, :not_found}

  @callback get_all() ::
              {:ok, [ExampleEntity.t()]} | {:error, String.t()}

  @callback save(ExampleEntity.t()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t()}

  @callback update(String.t(), map()) ::
              {:ok, ExampleEntity.t()} | {:error, String.t() | :not_found}

  @callback delete(String.t()) ::
              :ok | {:error, :not_found}
end
