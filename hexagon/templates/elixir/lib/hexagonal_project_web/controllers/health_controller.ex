defmodule HexagonalProjectWeb.HealthController do
  @moduledoc """
  Health check controller.
  """

  use Phoenix.Controller, namespace: HexagonalProjectWeb

  def check(conn, _params) do
    json(conn, %{
      status: "healthy",
      timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
    })
  end
end
