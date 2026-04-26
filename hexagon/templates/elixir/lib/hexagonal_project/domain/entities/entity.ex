defmodule HexagonalProject.Domain.Entities.ExampleEntity do
  @moduledoc """
  Example domain entity with state machine.
  """

  alias HexagonalProject.Domain.Errors

  @type status :: :pending | :active | :completed | :archived
  @type t :: %__MODULE__{
          id: String.t(),
          name: String.t(),
          description: String.t(),
          status: status(),
          created_at: DateTime.t(),
          updated_at: DateTime.t()
        }

  defstruct [:id, :name, :description, :status, :created_at, :updated_at]

  @doc """
  Creates a new example entity.
  """
  @spec create(String.t(), String.t(), String.t()) :: {:ok, t()} | {:error, String.t()}
  def create(id, name, description) do
    with :ok <- validate_name(name),
         :ok <- validate_description(description) do
      {:ok,
       %__MODULE__{
         id: id,
         name: name,
         description: description,
         status: :pending,
         created_at: DateTime.utc_now(),
         updated_at: DateTime.utc_now()
       }}
    end
  end

  @doc """
  Activates the entity.
  """
  @spec activate(t()) :: {:ok, t()} | {:error, String.t()}
  def activate(%__MODULE__{status: :pending} = entity) do
    {:ok, %{entity | status: :active, updated_at: DateTime.utc_now()}}
  end

  def activate(_entity) do
    {:error, "Can only activate pending entities"}
  end

  @doc """
  Completes the entity.
  """
  @spec complete(t()) :: {:ok, t()} | {:error, String.t()}
  def complete(%__MODULE__{status: :active} = entity) do
    {:ok, %{entity | status: :completed, updated_at: DateTime.utc_now()}}
  end

  def complete(_entity) do
    {:error, "Can only complete active entities"}
  end

  @doc """
  Archives the entity.
  """
  @spec archive(t()) :: {:ok, t()} | {:error, String.t()}
  def archive(%__MODULE__{status: status} = entity) when status in [:active, :completed] do
    {:ok, %{entity | status: :archived, updated_at: DateTime.utc_now()}}
  end

  def archive(_entity) do
    {:error, "Can only archive active or completed entities"}
  end

  defp validate_name(name) when is_binary(name) and byte_size(name) > 0 and byte_size(name) <= 100,
    do: :ok

  defp validate_name(_), do: {:error, "Name must be between 1 and 100 characters"}

  defp validate_description(description)
       when is_binary(description) and byte_size(description) <= 500,
       do: :ok

  defp validate_description(_), do: {:error, "Description must not exceed 500 characters"}
end
