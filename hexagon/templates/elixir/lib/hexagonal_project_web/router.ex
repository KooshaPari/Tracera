defmodule HexagonalProjectWeb.Router do
  @moduledoc """
  HTTP router for the web interface.
  """

  use Phoenix.Router

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", HexagonalProjectWeb do
    pipe_through :api

    get "/health", HealthController, :check
    get "/examples", ExampleController, :index
    get "/examples/:id", ExampleController, :show
    post "/examples", ExampleController, :create
    put "/examples/:id", ExampleController, :update
    delete "/examples/:id", ExampleController, :delete
    post "/examples/:id/activate", ExampleController, :activate
    post "/examples/:id/complete", ExampleController, :complete
  end
end
