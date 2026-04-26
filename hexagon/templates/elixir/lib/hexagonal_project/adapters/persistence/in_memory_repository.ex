defmodule HexagonalProject.Adapters.Persistence.InMemoryRepository do
  @moduledoc """
  In-memory implementation of the repository.
  """

  alias HexagonalProject.Domain.Entities.ExampleEntity
  alias HexagonalProject.Domain.Ports.Outbound

  @behaviour Outbound

  use Agent

  @impl true
  def start_link(_opts) do
    Agent.start_link(fn -> %{} end, name: __MODULE__)
  end

  @impl Outbound
  def get_by_id(id) do
    Agent.get(__MODULE__, fn state ->
      case Map.get(state, id) do
        nil -> {:error, :not_found}
        entity -> {:ok, entity}
      end
    end)
  end

  @impl Outbound
  def get_all() do
    Agent.get(__MODULE__, fn state ->
      {:ok, Map.values(state)}
    end)
  end

  @impl Outbound
  def save(entity) do
    Agent.update(__MODULE__, fn state ->
      Map.put(state, entity.id, entity)
    end)

    {:ok, entity}
  end

  @impl Outbound
  def update(id, attrs) do
    Agent.get_and_update(__MODULE__, fn state ->
      case Map.get(state, id) do
        nil ->
          {{:error, :not_found}, state}

        entity ->
          updated = struct(entity, attrs)
          {{:ok, updated}, Map.put(state, id, updated)}
      end
    end)
  end

  @impl Outbound
  def delete(id) do
    Agent.update(__MODULE__, fn state ->
      Map.delete(state, id)
    end)

    :ok
  end
end
