defmodule HexagonalProject.Application.ExampleService do
  @moduledoc """
  Application service for managing example entities.
  """

  alias HexagonalProject.Domain.Entities.ExampleEntity
  alias HexagonalProject.Domain.Ports.Outbound

  @behaviour HexagonalProject.Domain.Ports.Inbound

  defstruct [:repository]

  @type t :: %__MODULE__{
          repository: module()
        }

  @doc """
  Creates a new service instance.
  """
  def new(repository) do
    %__MODULE__{repository: repository}
  end

  @impl true
  def create_example(service, id, name, description) do
    with {:ok, entity} <- ExampleEntity.create(id, name, description),
         {:ok, saved} <- Outbound.save(service.repository, entity) do
      {:ok, saved}
    end
  end

  @impl true
  def get_example(service, id) do
    Outbound.get_by_id(service.repository, id)
  end

  @impl true
  def update_example(service, id, attrs) do
    Outbound.update(service.repository, id, attrs)
  end

  @impl true
  def delete_example(service, id) do
    Outbound.delete(service.repository, id)
  end

  @impl true
  def list_examples(service) do
    Outbound.get_all(service.repository)
  end

  @impl true
  def activate_example(service, id) do
    with {:ok, entity} <- Outbound.get_by_id(service.repository, id),
         {:ok, activated} <- ExampleEntity.activate(entity),
         {:ok, saved} <- Outbound.save(service.repository, activated) do
      {:ok, saved}
    end
  end

  @impl true
  def complete_example(service, id) do
    with {:ok, entity} <- Outbound.get_by_id(service.repository, id),
         {:ok, completed} <- ExampleEntity.complete(entity),
         {:ok, saved} <- Outbound.save(service.repository, completed) do
      {:ok, saved}
    end
  end
end
