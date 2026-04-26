defmodule HexagonalProjectWeb.ExampleController do
  @moduledoc """
  HTTP controller for example entities.
  """

  use Phoenix.Controller, namespace: HexagonalProjectWeb
  alias HexagonalProject.Application.ExampleService

  def index(conn, _params) do
    case ExampleService.list_examples() do
      {:ok, examples} ->
        json(conn, %{data: examples})

      {:error, reason} ->
        conn
        |> put_status(500)
        |> json(%{error: reason})
    end
  end

  def show(conn, %{"id" => id}) do
    case ExampleService.get_example(id) do
      {:ok, example} ->
        json(conn, %{data: example})

      {:error, :not_found} ->
        conn
        |> put_status(404)
        |> json(%{error: "Example not found"})
    end
  end

  def create(conn, params) do
    %{
      "id" => id,
      "name" => name,
      "description" => description
    } = params

    case ExampleService.create_example(id, name, description) do
      {:ok, example} ->
        conn
        |> put_status(201)
        |> json(%{data: example})

      {:error, :invalid_input} ->
        conn
        |> put_status(400)
        |> json(%{error: "Invalid input"})
    end
  end

  def update(conn, %{"id" => id} = params) do
    attrs = Map.take(params, ["name", "description"])

    case ExampleService.update_example(id, attrs) do
      {:ok, example} ->
        json(conn, %{data: example})

      {:error, :not_found} ->
        conn
        |> put_status(404)
        |> json(%{error: "Example not found"})
    end
  end

  def delete(conn, %{"id" => id}) do
    case ExampleService.delete_example(id) do
      :ok ->
        send_resp(conn, 204, "")

      {:error, :not_found} ->
        conn
        |> put_status(404)
        |> json(%{error: "Example not found"})
    end
  end

  def activate(conn, %{"id" => id}) do
    case ExampleService.activate_example(id) do
      {:ok, example} ->
        json(conn, %{data: example})

      {:error, :not_found} ->
        conn
        |> put_status(404)
        |> json(%{error: "Example not found"})

      {:error, :already_active} ->
        conn
        |> put_status(400)
        |> json(%{error: "Example already active"})
    end
  end

  def complete(conn, %{"id" => id}) do
    case ExampleService.complete_example(id) do
      {:ok, example} ->
        json(conn, %{data: example})

      {:error, :not_found} ->
        conn
        |> put_status(404)
        |> json(%{error: "Example not found"})

      {:error, :not_active} ->
        conn
        |> put_status(400)
        |> json(%{error: "Example must be active first"})
    end
  end
end
